from typing import List, NamedTuple, Set

import pytest

import dagger.when as when


def test__validate_when_clause_dependencies__with_correct_dependencies():
    cases = [
        (when.Always, {"x", "y", "z"}),
        (when.Equal("x", 1), {"x", "y", "z"}),
        (when.NotEqual("x", 1), {"x", "y", "z"}),
        (when.GreaterThan("x", 1), {"x", "y", "z"}),
        (when.LessThan("x", 1), {"x", "y", "z"}),
        (when.And(when.Equal("x", 1), when.Equal("y", 2)), {"x", "y", "z"}),
        (when.Or(when.Equal("x", 1), when.Equal("y", 2)), {"x", "y", "z"}),
        (when.Or(when.And(when.Equal("x", 1)), when.Equal("y", 2)), {"x", "y", "z"}),
    ]

    for case in cases:
        when.validate_when_clause_dependencies(*case)
        # we are asserting that no exceptions are raised


def test__validate_when_clause_dependencies__with_missing_dependencies():
    class Case(NamedTuple):
        clause: when.When
        node_inputs: Set[str]
        expected_missing_dependencies: List[str]

    cases = [
        Case(
            clause=when.Equal("x", 1),
            node_inputs=set(),
            expected_missing_dependencies=["x"],
        ),
        Case(
            clause=when.And(
                when.Equal("x", 1),
                when.NotEqual("y", 1),
                when.Or(when.GreaterThan("z", 1), when.LessThan("z", 100)),
            ),
            node_inputs=set(["a", "y"]),
            expected_missing_dependencies=["x", "z"],
        ),
    ]

    for case in cases:
        with pytest.raises(TypeError) as e:
            when.validate_when_clause_dependencies(case.clause, case.node_inputs)

        assert (
            str(e.value)
            == f"The when clause depends on the following parameters: {case.expected_missing_dependencies}. However, the node only declares the following inputs: {sorted(list(case[1]))}."
        )
