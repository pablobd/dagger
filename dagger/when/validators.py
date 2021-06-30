"""Validation functions for when clauses."""

from typing import Set, no_type_check

from dagger.when.protocol import When


def validate_when_clause_dependencies(clause: When, node_inputs: Set[str]):
    """
    Verify the when clause depends on parameters that have been declared as inputs to the node.

    Raises
    ------
    TypeError
        When the clause depends on parameters that haven't been specified as inputs to the node
    """
    missing_dependencies = _when_clause_dependencies(clause) - node_inputs

    if missing_dependencies:
        raise TypeError(
            f"The when clause depends on the following parameters: {sorted(list(missing_dependencies))}. However, the node only declares the following inputs: {sorted(list(node_inputs))}."
        )


@no_type_check
def _when_clause_dependencies(clause: When) -> Set[str]:
    if hasattr(clause, "conditions"):
        return set().union(
            *[_when_clause_dependencies(condition) for condition in clause.conditions]
        )
    elif hasattr(clause, "param_name"):
        return {clause.param_name}
    else:
        return set()
