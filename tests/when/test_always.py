from dagger.when.always import Always
from dagger.when.protocol import When


def test__conforms_to_protocol():
    assert isinstance(Always, When)
