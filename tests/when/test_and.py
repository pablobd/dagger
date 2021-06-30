import pytest

from dagger.when.and_ import And
from dagger.when.equal import Equal
from dagger.when.protocol import When


def test__conforms_to_protocol():
    assert isinstance(And(Equal("x", 1)), When)


def test__conditions():
    conditions = [Equal("x", 1), Equal("y", 2)]
    clause = And(*conditions)

    assert clause.conditions == conditions


def test__evaluate_condition_when_all_are_true():
    clause = And(Equal("x", 1), Equal("y", 2))
    assert clause.evaluate_condition({"x": 1, "y": 2})


def test__evaluate_condition_when_at_least_one_is_false():
    clause = And(Equal("x", 1), Equal("y", 2))
    assert not clause.evaluate_condition({"x": 1, "y": 1})


def test__when_any_condition_raises_an_error():
    clause = And(Equal("existing", 1), Equal("missing", 2))

    with pytest.raises(ValueError) as e:
        clause.evaluate_condition({"existing": 1})

    assert (
        str(e.value)
        == "Parameter 'missing' was expected to be equal to '2' (type: int). However, no parameter with that name was passed to this node. The node received the following parameters ['existing']"
    )
