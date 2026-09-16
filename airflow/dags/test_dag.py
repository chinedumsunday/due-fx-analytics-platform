import json
import requests
import datetime
from airflow.sdk import dag, task
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.sdk import get_current_context
from datetime import datetime as dt
from alerts import notify_failure, notify_sla_miss
from datetime import timedelta
# import pandas as pd

@dag(
    dag_id = "test_dag",
    schedule = "@daily",
    start_date = datetime.datetime(2026, 7, 1),
    catchup = False,
    on_failure_callback=notify_failure,
    tags = ["test", "ingestion"],
        default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "sla": timedelta(hours=1),
    },
    sla_miss_callback=notify_sla_miss
)
def test_dag():
    @task()
    def get_full_context():
        ctx = get_current_context()
        print(ctx.keys())
    get_full_context()

test_dag()



