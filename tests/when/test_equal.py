import pytest

from dagger.when.equal import Equal
from dagger.when.protocol import When


def test__conforms_to_protocol():
    assert isinstance(Equal("param", "value"), When)


def test__when_param_name_is_not_among_supplied_parameters():
    clause = Equal("missing", "value")

    with pytest.raises(ValueError) as e:
        clause.evaluate_condition({"another": "parameter"})

    assert (
        str(e.value)
        == "Parameter 'missing' was expected to be equal to 'value' (type: str). However, no parameter with that name was passed to this node. The node received the following parameters ['another']"
    )


def test__param_name():
    param_name = "some-name"
    assert Equal(param_name, 1).param_name == param_name


def test__value():
    value = 6
    assert Equal("name", value).value == value


def test__evaluate_condition_when_equal():
    param_name = "some-name"
    assert Equal(param_name, 1).evaluate_condition({param_name: 1})


def test__evaluate_condition_when_not_equal():
    param_name = "some-name"
    assert not Equal(param_name, 1).evaluate_condition({param_name: 2})
