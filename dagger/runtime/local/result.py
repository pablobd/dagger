"""Data structure representing the result of running a task."""

from typing import Mapping, NamedTuple, Union


class Succeeded(NamedTuple):
    """Represents the successful execution of a node."""

    outputs: Mapping[str, bytes]


class Skipped(NamedTuple):
    """Represents the skipping of a node due to its 'when' clause."""

    cause: str


Result = Union[Succeeded, Skipped]
