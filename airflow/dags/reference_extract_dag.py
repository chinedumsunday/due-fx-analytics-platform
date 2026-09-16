import datetime
from airflow.sdk import dag, task
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.sdk import get_current_context
from datetime import datetime as dt
from airflow.providers.postgres.hooks.postgres import PostgresHook
from io import BytesIO
from alerts import notify_failure, notify_sla_miss
from datetime import timedelta


tables = ["users", "corridors"]

@dag(
    dag_id = "reference_extract_dag",
    schedule = "@daily",
    start_date = datetime.datetime(2026, 7, 1),
    catchup = False,
    tags = ["reference", "ingestion"],
    on_failure_callback=notify_failure,
        default_args={
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "sla": timedelta(hours=1),
    },
    sla_miss_callback=notify_sla_miss
)

def reference_extract_dag():
    @task()
    def extract_reference_data():
        ctx = get_current_context()
        ds = ctx["ds"]
        for table in tables:
            hook = PostgresHook(postgres_conn_id="postgres_default")
            sql = f"SELECT * FROM {table}"
            df = hook.get_pandas_df(sql)
            assert not df.empty, f"No Entry found in {table}"
            buffer = BytesIO()
            df.to_parquet(buffer, index=False)
            hook2 = GCSHook(gcp_conn_id="google_cloud_default")
            object_name = f"raw/{table}/date={ds}/{table}.parquet"
            hook2.upload(bucket_name="due-fx-data-245535", object_name=object_name, data=buffer.getvalue())
            print(f"{table}: {len(df)} rows")
    extract_reference_data()

reference_extract_dag()