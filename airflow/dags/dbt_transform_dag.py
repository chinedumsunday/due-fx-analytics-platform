import datetime
from datetime import timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.sensors.external_task import ExternalTaskSensor
from airflow.sdk import dag
from alerts import notify_failure, notify_sla_miss

DBT_DIR = "/opt/airflow/dbt"


@dag(
    dag_id="dbt_transform_dag",
    schedule="0 3 * * *",
    start_date=datetime.datetime(2026, 9, 1, tzinfo=datetime.timezone.utc),
    catchup=False,
    tags=["dbt", "transform"],
    on_failure_callback=notify_failure,
    default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "sla": timedelta(hours=1),
    },
    sla_miss_callback=notify_sla_miss
)
def dbt_transform_dag():

    wait_for_cbn = ExternalTaskSensor(
        task_id="wait_for_cbn",
        external_dag_id="cbn_rates_dag",
        external_task_id="validate_cbn_rates",
        execution_delta=timedelta(hours=3),
        mode="reschedule",
        poke_interval=300,
        timeout=3600,
        allowed_states=["success"],
        failed_states=["failed", "skipped"],
    )

    wait_for_parallel = ExternalTaskSensor(
        task_id="wait_for_parallel",
        external_dag_id="parallel_rates_dag",
        external_task_id="validate_parallel_rates",
        execution_delta=timedelta(hours=1),
        mode="reschedule",
        poke_interval=300,
        timeout=3600,
        allowed_states=["success"],
        failed_states=["failed", "skipped"],
    )

    wait_for_reference = ExternalTaskSensor(
        task_id="wait_for_reference",
        external_dag_id="reference_extract_dag",
        external_task_id="extract_reference_data",
        execution_delta=timedelta(hours=3),
        mode="reschedule",
        poke_interval=300,
        timeout=3600,
        allowed_states=["success"],
        failed_states=["failed", "skipped"],
    )

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"cd {DBT_DIR} && dbt deps",
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"cd {DBT_DIR} && dbt seed",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {DBT_DIR} && dbt build",
    )

    [wait_for_cbn, wait_for_parallel, wait_for_reference] >> dbt_deps
    dbt_deps >> dbt_seed >> dbt_build


dbt_transform_dag()