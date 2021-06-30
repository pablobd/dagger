"""Compare the value of a node input with a value and expect the input to be less than the value."""

from typing import Any, Dict


class LessThan:
    """Compare the value of a node input with a value and expect the input to be less than the value."""

    def __init__(
        self,
        param_name: str,
        value: Any,
    ):
        """
        Initialize a LessThan when clause.

        Parameters
        ----------
        param_name
            The name of the node parameter to compare against

        value
            The value we're expecting the parameter to be less then, once deserialized

        Returns
        -------
        A valid implementation of the 'When' protocol
        """
        self._param_name = param_name
        self._value = value

    @property
    def param_name(self) -> str:
        """Get the parameter name associated with the clause."""
        return self._param_name

    @property
    def value(self) -> Any:
        """Get the value associated with the clause."""
        return self._value

    def evaluate_condition(self, params: Dict[str, Any]) -> bool:
        """
        Return true if the parameter is less than the specified value.

        Raises
        ------
        ValueError
            When the parameter name is not among the parameters supplied to the node.

        TypeError
            When the parameter value is incompatible with the clause value (e.g. we are trying to compare a string with an integer)
        """
        if self._param_name not in params:
            raise ValueError(
                f"Parameter '{self._param_name}' was expected to be less than '{self._value}' (type: {type(self._value).__name__}). However, no parameter with that name was passed to this node. The node received the following parameters {list(params)}"
            )

        try:
            return params[self._param_name] < self._value
        except TypeError:
            raise TypeError(
                f"Parameter '{self._param_name}' was expected to be less than '{self._value}' (type: {type(self._value).__name__}). However, the type of parameter '{self._param_name}' was '{type(params[self._param_name]).__name__}', which is incompatible. For this condition to work you will need to supply a parameter value that matches the one specified in the condition."
            )
