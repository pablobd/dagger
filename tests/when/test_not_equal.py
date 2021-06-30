import pytest

from dagger.when.not_equal import NotEqual
from dagger.when.protocol import When


def test__conforms_to_protocol():
    assert isinstance(NotEqual("param", "value"), When)


def test__when_param_name_is_not_among_supplied_parameters():
    clause = NotEqual("missing", "value")

    with pytest.raises(ValueError) as e:
        clause.evaluate_condition({"another": "parameter"})

    assert (
        str(e.value)
        == "Parameter 'missing' was expected to not be equal to 'value' (type: str). However, no parameter with that name was passed to this node. The node received the following parameters ['another']"
    )


def test__param_name():
    param_name = "some-name"
    assert NotEqual(param_name, 1).param_name == param_name


def test__value():
    value = 6
    assert NotEqual("name", value).value == value


def test__evaluate_condition_when_equal():
    param_name = "some-name"
    assert NotEqual(param_name, 1).evaluate_condition({param_name: 2})


def test__evaluate_condition_when_not_equal():
    param_name = "some-name"
    assert not NotEqual(param_name, 1).evaluate_condition({param_name: 1})
