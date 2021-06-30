"""
# Conditional execution.

This DAG shows how to define tasks that only execute when a certain condition is met.


## Behavior

We define a task that flips a coin. Then, we add 2 extra tasks, each with a conditional clause that determines they will only be executed if the coin flip returned a specific result.


## Implementation

We add a "when" clause to the tasks we want to run conditionally. When clauses analyze the task inputs to determine whether or not to execute it. Several strategies are provided in the `dagger.when` package.

Specifying conditionals using "when", instead of a simple "if-else" in the body of the function comes in handy for several reasons:

* Sometimes, you may want to skip the execution of a nested DAG, and you don't want to repeat the conditional in all the tasks of that DAG.
* Conditional executions are a native construct of many runtimes (such as Argo). These runtimes may be able to save resources when there are many tasks that should run conditionally. They may also have specific visual representations for skipped tasks that would help you understand how a DAG was executed.
"""

import random

import dagger.input as input
import dagger.output as output

# import dagger.when as when
from dagger import DAG, Task


def flip_coin() -> str:  # noqa
    return random.choice(["heads", "tails"])


def announce_result(coin_result):  # noqa
    print(f"It was {coin_result}!")


dag = DAG(
    nodes={
        "flip-coin": Task(
            flip_coin,
            outputs={
                "result": output.FromReturnValue(),
            },
        ),
        "announce-heads": Task(
            announce_result,
            inputs={
                "coin_result": input.FromNodeOutput("flip-coin", "result"),
            },
            # when=when.Equal("coin_result", "heads"),
        ),
        "announce-tails": Task(
            announce_result,
            inputs={
                "coin_result": input.FromNodeOutput("flip-coin", "result"),
            },
            # when=when.NotEqual("coin_result", "heads"),
        ),
    },
)


def run_from_cli():
    """Define a command-line interface for this DAG, using the CLI runtime. Check the documentation to understand why this is relevant or necessary."""
    from dagger.runtime.cli import invoke

    invoke(dag)
