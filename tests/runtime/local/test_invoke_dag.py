import pytest

from dagger.dag import DAG
from dagger.input import FromNodeOutput, FromParam
from dagger.output import FromKey, FromReturnValue
from dagger.runtime.local import invoke
from dagger.task import Task


def test__invoke_dag__with_no_inputs_or_outputs():
    invocations = []
    dag = DAG(
        {
            "single-task": Task(lambda: invocations.append(1)),
        }
    )
    assert invoke(dag) == {}
    assert invocations == [1]


def test__invoke_dag__with_inputs_and_outputs():
    dag = DAG(
        nodes=dict(
            square=Task(
                lambda x: x ** 2,
                inputs=dict(x=FromParam()),
                outputs=dict(x_squared=FromReturnValue()),
            ),
        ),
        inputs=dict(x=FromParam()),
        outputs=dict(x_squared=FromNodeOutput("square", "x_squared")),
    )
    assert invoke(dag, params=dict(x=3)) == dict(x_squared=b"9")


def test__invoke_dag__with_missing_input_parameter():
    dag = DAG(
        nodes=dict(one=Task(lambda: 1)),
        inputs=dict(a=FromParam()),
    )
    with pytest.raises(ValueError) as e:
        invoke(dag, params=dict(y=3))

    assert (
        str(e.value)
        == "The parameters supplied to this DAG were supposed to contain the following parameters: ['a']. However, only the following parameters were actually supplied: ['y']. We are missing: ['a']."
    )


def test__invoke_dag__mapping_dag_parameters_to_node_inputs():
    dag = DAG(
        inputs=dict(a=FromParam()),
        outputs=dict(x=FromNodeOutput("times3", "x")),
        nodes=dict(
            times3=Task(
                lambda b: b * 3,
                inputs=dict(b=FromParam("a")),
                outputs=dict(x=FromReturnValue()),
            )
        ),
    )

    assert invoke(dag, params=dict(a=1)) == {"x": b"3"}


def test__invoke_dag__propagates_task_exceptions_extending_the_details():
    dag = DAG(
        nodes=dict(
            square=Task(
                lambda x: x ** 2,
                inputs=dict(x=FromParam()),
                outputs=dict(x_squared=FromKey("missing-key")),
            ),
        ),
        inputs=dict(x=FromParam()),
    )
    with pytest.raises(TypeError) as e:
        invoke(dag, params=dict(x=3))

    assert (
        str(e.value)
        == "Error when invoking node 'square'. We encountered the following error while attempting to serialize the results of this task: This output is of type FromKey. This means we expect the return value of the function to be a mapping containing, at least, a key named 'missing-key'"
    )


def test__invoke_dag__invokes_nodes_in_the_right_order_based_on_their_dependencies():
    dag = DAG(
        nodes={
            "square-number": Task(
                lambda n: n ** 2,
                inputs=dict(n=FromNodeOutput("generate-number", "n")),
                outputs=dict(n=FromReturnValue()),
            ),
            "divide-number-by-three": Task(
                lambda n: n // 3,
                inputs=dict(n=FromNodeOutput("square-number", "n")),
                outputs=dict(n=FromReturnValue()),
            ),
            "generate-number": Task(
                lambda: 9,
                outputs=dict(n=FromReturnValue()),
            ),
        },
        outputs=dict(n=FromNodeOutput("divide-number-by-three", "n")),
    )
    assert invoke(dag) == dict(n=b"27")


def test__invoke_dag__with_nested_dags():
    dag = DAG(
        {
            "outermost": DAG(
                {
                    "come-up-with-a-number": Task(
                        lambda: 1, outputs=dict(x=FromReturnValue())
                    ),
                    "middle": DAG(
                        {
                            "innermost": Task(
                                lambda x: 2 * x,
                                inputs=dict(x=FromParam()),
                                outputs=dict(y=FromReturnValue()),
                            )
                        },
                        inputs=dict(x=FromNodeOutput("come-up-with-a-number", "x")),
                        outputs=dict(yy=FromNodeOutput("innermost", "y")),
                    ),
                },
                outputs=dict(yyy=FromNodeOutput("middle", "yy")),
            )
        },
        outputs=dict(yyyy=FromNodeOutput("outermost", "yyy")),
    )

    assert invoke(dag) == dict(yyyy=b"2")


def test__invoke_dag__with_dynamic_partitions():
    dag = DAG(
        {
            "generate-partitions": Task(
                lambda: ["a", "b", "c"],
                outputs=dict(letters=FromReturnValue(is_partitioned=True)),
            ),
            "run-for-each-partition": Task(
                lambda letter: f"letter '{letter}'",
                inputs=dict(letter=FromNodeOutput("generate-partitions", "letters")),
                outputs=dict(message=FromReturnValue()),
                partition_by_input="letter",
            ),
            "gather-messages": Task(
                lambda messages: f"Got messages: {', and '.join(messages)}.",
                inputs=dict(
                    messages=FromNodeOutput("run-for-each-partition", "message")
                ),
                outputs=dict(result=FromReturnValue()),
            ),
        },
        outputs=dict(result=FromNodeOutput("gather-messages", "result")),
    )

    assert invoke(dag) == dict(
        result=b"\"Got messages: letter 'a', and letter 'b', and letter 'c'.\""
    )


def test__invoke_dag__with_partitioned_output():
    dag = DAG(
        outputs=dict(result=FromNodeOutput("fan-out", "numbers")),
        nodes={
            "fan-out": Task(
                lambda: [1, 2, 3],
                outputs={
                    "numbers": FromReturnValue(is_partitioned=True),
                },
            ),
        },
    )

    assert list(invoke(dag)["result"]) == [b"1", b"2", b"3"]


def test__invoke_dag__with_partitions_but_invalid_outputs():
    dag = DAG(
        nodes={
            "generate-single-number": Task(
                lambda: 1,
                outputs={"n": FromReturnValue()},
            ),
            "poorly-partitioned-task": Task(
                lambda x: x,
                inputs=dict(x=FromNodeOutput("generate-single-number", "n")),
                partition_by_input="x",
            ),
        },
    )

    with pytest.raises(TypeError) as e:
        invoke(dag)

    assert (
        str(e.value)
        == "Error when invoking node 'poorly-partitioned-task'. This node is supposed to be partitioned by input 'x'. When a node is partitioned, the value of the input that determines the partition should be an iterable. Instead, we found a value of type 'int'."
    )
