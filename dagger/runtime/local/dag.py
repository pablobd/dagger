"""Run a DAG in memory."""
import itertools
from typing import Dict, Mapping, Optional, Union

from dagger.dag import DAG, Node
from dagger.dag import SupportedInputs as SupportedDAGInputs
from dagger.dag import validate_parameters
from dagger.input import FromNodeOutput, FromParam
from dagger.runtime.local.io import _deserialize_inputs
from dagger.runtime.local.result import Result, Skipped, Succeeded
from dagger.runtime.local.task import invoke_task
from dagger.serializer import SerializationError
from dagger.task import SupportedInputs as SupportedTaskInputs


def invoke_dag(
    dag: DAG,
    params: Optional[Mapping[str, bytes]] = None,
) -> Result:
    """
    Invoke a DAG with a series of parameters.

    Parameters
    ----------
    dag
        DAG to execute

    params
        Inputs to the DAG.
        Serialized into their binary format.
        Indexed by input/parameter name.


    Returns
    -------
    The result of the execution, which can be:
    - Succeeded, with the serialized outputs of the DAG, indexed by output name.
    - Skipped, if the DAG was skipped due to its 'when' clause.


    Raises
    ------
    ValueError
        When any required parameters are missing

    TypeError
        When any of the outputs cannot be obtained from the return value of their node

    SerializationError
        When some of the outputs cannot be serialized with the specified Serializer
    """
    params = params or {}
    outputs: Dict[str, Result] = {}

    validate_parameters(dag.inputs, params)

    inputs = _deserialize_inputs(inputs=dag.inputs, params=params)
    if not dag.when.evaluate_condition(inputs):
        return Skipped(cause="When clause evaluated to False")

    # TODO: Support both sequential and parallel execution
    sequential_node_order = itertools.chain(*dag.node_execution_order)
    for node_name in sequential_node_order:
        node = dag.nodes[node_name]
        node_params_result = _retrieve_node_params(
            node_name=node_name,
            node_inputs=node.inputs,
            outputs=outputs,
            params=params,
        )
        if isinstance(node_params_result, Skipped):
            outputs[node_name] = node_params_result
            continue
        else:
            outputs[node_name] = _invoke_dag_or_task(
                node_name=node_name,
                node=node,
                node_params=node_params_result,
            )

    dag_outputs = {}
    for output_name in dag.outputs:
        output_type = dag.outputs[output_name]
        node_result = outputs[output_type.node]
        if isinstance(node_result, Succeeded):
            dag_outputs[output_name] = node_result.outputs[output_type.output]
        else:
            return Skipped(
                f"DAG output depends on the result of node '{output_type.node}', which was skipped due to: {node_result.cause}"
            )

    return Succeeded(outputs=dag_outputs)


def _retrieve_node_params(
    node_name: str,
    node_inputs: Mapping[str, Union[SupportedDAGInputs, SupportedTaskInputs]],
    outputs: Mapping[str, Result],
    params: Mapping[str, bytes],
) -> Union[Mapping[str, bytes], Skipped]:

    node_params: Dict[str, bytes] = {}

    for input_name in node_inputs:
        node_input = node_inputs[input_name]
        if isinstance(node_input, FromParam):
            node_params[input_name] = params[input_name]
        elif isinstance(node_input, FromNodeOutput):
            node_result = outputs[node_input.node]
            if isinstance(node_result, Succeeded):
                node_params[input_name] = node_result.outputs[node_input.output]
            else:
                return Skipped(
                    f"Node '{node_name}' depends on the outputs of node '{node_input.node}', but '{node_input.node}' was skipped due to: {node_result.cause}"
                )

        else:
            raise TypeError(
                f"Input type '{type(node_input)}' is not supported by the local runtime. The use of unsupported inputs should have been validated by the DAG object. This may be a bug in the library. Please open an issue in our GitHub repository."
            )

    return node_params


def _invoke_dag_or_task(
    node_name: str,
    node: Node,
    node_params: Mapping[str, bytes],
) -> Result:
    try:
        if isinstance(node, DAG):
            return invoke_dag(node, params=node_params)
        else:
            return invoke_task(node, params=node_params)
    except (ValueError, TypeError, SerializationError) as e:
        raise e.__class__(f"Error when invoking node '{node_name}'. {str(e)}")
