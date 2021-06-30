"""Protocol all when clauses should conform to."""

from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class When(Protocol):
    """Protocol all when clauses conform to."""

    def evaluate_condition(self, params: Dict[str, Any]) -> bool:
        """
        Evaluate the condition for a when clause, given the parameters to a node.

        Raises
        ------
        ValueError
            When the clause doesn't match the supplied parameters.

        TypeError
            When the parameter value has an incompatible type with the one expected by the clause.
        """
        ...
