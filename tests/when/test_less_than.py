import pytest

from dagger.when.less_than import LessThan
from dagger.when.protocol import When


def test__conforms_to_protocol():
    assert isinstance(LessThan("param", 1), When)


def test__when_param_name_is_not_among_supplied_parameters():
    clause = LessThan("missing", 1.5)

    with pytest.raises(ValueError) as e:
        clause.evaluate_condition({"another": 1.0})

    assert (
        str(e.value)
        == "Parameter 'missing' was expected to be less than '1.5' (type: float). However, no parameter with that name was passed to this node. The node received the following parameters ['another']"
    )


def test__when_param_value_is_incompatible_with_clause_value():
    clause = LessThan("x", 2)

    with pytest.raises(TypeError) as e:
        clause.evaluate_condition({"x": "incompatible-type"})

    assert (
        str(e.value)
        == "Parameter 'x' was expected to be less than '2' (type: int). However, the type of parameter 'x' was 'str', which is incompatible. For this condition to work you will need to supply a parameter value that matches the one specified in the condition."
    )


def test__param_name():
    param_name = "some-name"
    assert LessThan(param_name, 1).param_name == param_name


def test__value():
    value = 6
    assert LessThan("name", value).value == value


def test__evaluate_condition_when_less_than():
    cases = [
        {"param": 0, "less_than_value": 1},
        {"param": 1.1, "less_than_value": 1.2},
        {"param": 1.5, "less_than_value": 2},
        {"param": 1, "less_than_value": 2.2},
        {"param": "a", "less_than_value": "z"},
    ]
    for case in cases:
        assert LessThan("param", case["less_than_value"]).evaluate_condition(
            {"param": case["param"]}
        )


def test__evaluate_condition_when_not_less_than():
    cases = [
        {"param": 1, "less_than_value": 1},
        {"param": 1.1, "less_than_value": 1.1},
        {"param": 2.5, "less_than_value": 2},
        {"param": 3, "less_than_value": 2.5},
        {"param": "z", "less_than_value": "a"},
    ]
    for case in cases:
        assert not LessThan("param", case["less_than_value"]).evaluate_condition(
            {"param": case["param"]}
        )
