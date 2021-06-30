"""Run tasks in memory."""
from typing import Mapping, Optional

from dagger.runtime.local.io import _deserialize_inputs, _serialize_outputs
from dagger.runtime.local.result import Result, Skipped, Succeeded
from dagger.task import Task


def invoke_task(
    task: Task,
    params: Optional[Mapping[str, bytes]] = None,
) -> Result:
    """
    Invoke a task with a series of parameters.

    Parameters
    ----------
    task
        Task to execute

    params
        Inputs to the task.
        Serialized into their binary format.
        Indexed by input/parameter name.


    Returns
    -------
    The result of the execution, which can be:
    - Succeeded, with the serialized outputs of the task, indexed by output name.
    - Skipped, if the task was skipped due to its 'when' clause.


    Raises
    ------
    ValueError
        When any required parameters are missing

    TypeError
        When any of the outputs cannot be obtained from the return value of the task's function

    SerializationError
        When some of the outputs cannot be serialized with the specified Serializer
    """
    params = params or {}

    inputs = _deserialize_inputs(
        inputs=task.inputs,
        params=params,
    )

    if not task.when.evaluate_condition(inputs):
        return Skipped(cause="When clause evaluated to False")

    return_value = task.func(**inputs)

    return Succeeded(
        outputs=_serialize_outputs(outputs=task.outputs, return_value=return_value),
    )
