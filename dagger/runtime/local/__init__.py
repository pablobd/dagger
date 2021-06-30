"""Run DAGs or nodes in memory."""

from dagger.runtime.local.dag import invoke_dag  # noqa
from dagger.runtime.local.result import Result, Skipped, Succeeded  # noqa
from dagger.runtime.local.task import invoke_task  # noqa
