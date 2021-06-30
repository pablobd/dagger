import pytest

from dagger.when.equal import Equal
from dagger.when.or_ import Or
from dagger.when.protocol import When


def test__conforms_to_protocol():
    assert isinstance(Or(Equal("x", 1)), When)


def test__conditions():
    conditions = [Equal("x", 1), Equal("y", 2)]
    clause = Or(*conditions)

    assert clause.conditions == conditions


def test__evaluate_condition_when_all_are_false():
    clause = Or(Equal("x", 1), Equal("y", 2))
    assert not clause.evaluate_condition({"x": 11, "y": 22})


def test__evaluate_condition_when_at_least_one_is_true():
    clause = Or(Equal("x", 1), Equal("y", 2))
    assert clause.evaluate_condition({"x": 1, "y": 1})


def test__when_any_condition_raises_an_error():
    clause = Or(Equal("existing", 2), Equal("missing", 2))

    with pytest.raises(ValueError) as e:
        clause.evaluate_condition({"existing": 1})

    assert (
        str(e.value)
        == "Parameter 'missing' was expected to be equal to '2' (type: int). However, no parameter with that name was passed to this node. The node received the following parameters ['existing']"
    )
