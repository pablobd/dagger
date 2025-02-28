import pytest

from dagger.serializer.as_json import AsJSON
from dagger.serializer.errors import DeserializationError, SerializationError
from dagger.serializer.protocol import Serializer


def test__conforms_to_protocol():
    assert isinstance(AsJSON(), Serializer)


def test_extension():
    assert AsJSON().extension == "json"


def test_serialization_and_deserialization__with_valid_values():
    serializer = AsJSON()
    valid_values = [
        None,
        1,
        1.1,
        True,
        "string",
        ["list", "of", 3],
        {"object": {"with": ["nested", "values"]}},
    ]

    for value in valid_values:
        serialized_value = serializer.serialize(value)
        assert (type(serialized_value)) == bytes

        deserialized_value = serializer.deserialize(serialized_value)
        assert value == deserialized_value


def test_serialization__with_indentation():
    serializer = AsJSON(indent=2)
    serialized_value = serializer.serialize({"a": 1, "b": 2})
    assert serialized_value == b'{\n  "a": 1,\n  "b": 2\n}'


def test_serialization__with_invalid_values():
    serializer = AsJSON()
    invalid_values = [
        float("inf"),
        float("-inf"),
        float("nan"),
        {"python", "set"},
        serializer,
    ]

    for value in invalid_values:
        with pytest.raises(SerializationError):
            serializer.serialize(value)


def test_deserialization__with_invalid_values():
    serializer = AsJSON()
    invalid_values = [
        {"python": ["data", "structure"]},
        serializer,
    ]

    for value in invalid_values:
        with pytest.raises(DeserializationError):
            serializer.deserialize(value)
