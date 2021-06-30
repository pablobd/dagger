"""Compare the value of a node input with a literal."""

from typing import Any, Dict


class Equal:
    """Compare the value of a node input with a literal."""

    def __init__(
        self,
        param_name: str,
        value: Any,
    ):
        """
        Initialize an Equal when clause.

        Parameters
        ----------
        param_name
            The name of the node parameter to compare against

        value
            The value we're expecting the parameter to be equal to, once deserialized

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
        Return true if the parameter is equal to the specified value.

        Raises
        ------
        ValueError
            When the parameter name is not among the parameters supplied to the node.
        """
        if self._param_name not in params:
            raise ValueError(
                f"Parameter '{self._param_name}' was expected to be equal to '{self._value}' (type: {type(self._value).__name__}). However, no parameter with that name was passed to this node. The node received the following parameters {list(params)}"
            )

        return params[self._param_name] == self._value
