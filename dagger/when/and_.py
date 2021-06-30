"""Evaluate several conditions and return true if all of them are true."""

from typing import Any, Dict, List

from dagger.when.protocol import When


class And:
    """Evaluate several conditions and return true if all of them are true."""

    def __init__(
        self,
        *conditions: When,
    ):
        """
        Initialize an And when clause.

        Parameters
        ----------
        conditions
            An arbitrary number of conditions to apply the "and" operation to.


        Returns
        -------
        A valid implementation of the 'When' protocol
        """
        self._conditions = conditions

    @property
    def conditions(self) -> List[When]:
        """Return a copy of the conditions for this clause."""
        return list(self._conditions)[:]

    def evaluate_condition(self, params: Dict[str, Any]) -> bool:
        """
        Return true if all the conditions evaluate to true.

        Raises
        ------
        ValueError
            If any of the conditions raise it.
        """
        for condition in self._conditions:
            if not condition.evaluate_condition(params):
                return False

        return True
