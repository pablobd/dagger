"""Functions to serialize and deserialize inputs/outputs."""

from typing import Any, Mapping, Union

from dagger.dag import SupportedInputs as SupportedDAGInputs
from dagger.serializer import SerializationError
from dagger.task import SupportedInputs as SupportedTaskInputs
from dagger.task import SupportedOutputs as SupportedTaskOutputs


def _deserialize_inputs(
    inputs: Union[
        Mapping[str, SupportedDAGInputs],
        Mapping[str, SupportedTaskInputs],
    ],
    params: Mapping[str, bytes],
):

    deserialized_inputs = {}
    for input_name in inputs:
        try:
            deserialized_inputs[input_name] = inputs[input_name].serializer.deserialize(
                params[input_name]
            )
        except KeyError:
            raise ValueError(
                f"The parameters supplied to this task were supposed to contain a parameter named '{input_name}', but only the following parameters were actually supplied: {list(params.keys())}"
            )

    return deserialized_inputs


def _serialize_outputs(
    outputs: Mapping[str, SupportedTaskOutputs],
    return_value: Any,
) -> Mapping[str, bytes]:

    serialized_outputs = {}
    for output_name in outputs:
        output_type = outputs[output_name]
        try:
            output = output_type.from_function_return_value(return_value)
            serialized_outputs[output_name] = output_type.serializer.serialize(output)
        except (TypeError, ValueError, SerializationError) as e:
            raise e.__class__(
                f"We encountered the following error while attempting to serialize the results of this task: {str(e)}"
            )

    return serialized_outputs
