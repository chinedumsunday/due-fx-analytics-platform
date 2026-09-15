import json
import requests
import datetime
from airflow.sdk import dag, task
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.sdk import get_current_context
from datetime import datetime as dt
# import pandas as pd

@dag(
    dag_id = "test_dag",
    schedule = "@daily",
    start_date = datetime.datetime(2026, 7, 1),
    catchup = False,
    tags = ["test", "ingestion"],
)
def test_dag():
    @task()
    def get_full_context():
        ctx = get_current_context()
        print(ctx.keys())
    get_full_context()

test_dag()



