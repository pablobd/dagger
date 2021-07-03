from examples.conditional_execution import dag
from tests.examples.verification import verify_dag_works_with_all_runtimes


def test():
    verify_dag_works_with_all_runtimes(
        dag,
        params={
            "announce": b"true",
        },
        validate_results=lambda _results: None,
        argo_workflow_yaml_filename="conditional_execution.yaml",
    )
