import datetime
from airflow.sdk import dag, task
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.sdk import get_current_context
from datetime import datetime as dt, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook
from io import BytesIO
from airflow.sdk.exceptions import AirflowSkipException

LOOKBACK = timedelta(minutes=2)

@dag(
    dag_id = "transactions_extract_dag",
    schedule = LOOKBACK,
    start_date = datetime.datetime(2026, 7, 1),
    catchup = False,
    tags = ["transactions", "ingestion"],
)
def transactions_extract_dag():
    @task()
    def extract_and_land_transactions():
        ctx = get_current_context()
        data_interval_end = ctx["data_interval_end"]
        data_interval_start = data_interval_end - LOOKBACK
        hook = PostgresHook(postgres_conn_id="postgres_default")
        sql_query = "SELECT * FROM transactions WHERE updated_at >= %s AND updated_at < %s"
        df = hook.get_pandas_df(sql_query, parameters=(data_interval_start, data_interval_end))
        if df.empty:
            raise AirflowSkipException(f"No transactions found between {data_interval_start} and {data_interval_end}")
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        hook2 = GCSHook(gcp_conn_id="google_cloud_default")
        object_name = f"raw/transactions/date={data_interval_start.date()}/transactions_{data_interval_start.strftime('%H%M%S')}_{data_interval_end.strftime('%H%M%S')}.parquet"
        hook2.upload(bucket_name="due-fx-data-245535", object_name=object_name, data=buffer.getvalue())
        print(f"Uploaded {len(df)} records to GCS at {object_name}")
        print(df.shape)
        print(df.columns)
        print(f"Data interval start: {data_interval_start}")
        print(f"Data interval end: {data_interval_end}")
        return object_name
    extract_and_land_transactions()

transactions_extract_dag()