"""When clause that always returns true."""

from typing import Any, Dict


class AlwaysSingleton:
    """Always return true (this is the default when clause for all nodes)."""

    def evaluate_condition(self, params: Dict[str, Any]) -> bool:
        """Return true."""
        return True


Always = AlwaysSingleton()
