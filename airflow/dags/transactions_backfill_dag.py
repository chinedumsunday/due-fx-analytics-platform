import datetime
from airflow.sdk import dag, task
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import get_current_context
from io import BytesIO
from datetime import datetime as dt

cutover = dt.fromisoformat("2026-09-03 20:52:04+00")

@dag(
    dag_id = "backfill_transactions_dag",
    schedule = None,
    catchup = False,
    start_date = datetime.datetime(2026, 7, 1),
    tags = ["transactions", "backfill"],
)
def backfill_transactions_dag():
    @task()
    def date_list():
        hook = PostgresHook(postgres_conn_id="postgres_default")
        sql = "SELECT DISTINCT DATE(updated_at) FROM transactions WHERE updated_at < %s ORDER BY DATE(updated_at) DESC"
        dates = hook.get_records(sql, (cutover,))
        return [d[0].strftime("%Y-%m-%d") for d in dates]

    @task()
    def backfill_transactions(dates):
        hook2 = PostgresHook(postgres_conn_id="postgres_default")
        for date in dates: 
            sql = "SELECT * FROM transactions WHERE updated_at >= DATE(%s) AND updated_at < DATE(%s) + INTERVAL '1 day'"
            transactions = hook2.get_pandas_df(sql, (date, date))
            if transactions.empty:
                print(f"No transactions found for {date}")
                continue
            buffer = BytesIO()
            transactions.to_parquet(buffer, index=False)
            hook3 = GCSHook(gcp_conn_id="google_cloud_default")
            object_name = f"raw/transactions/date={date}/backfill.parquet"
            hook3.upload(bucket_name="due-fx-data-245535", object_name=object_name, data=buffer.getvalue())
            print(f"Uploaded {len(transactions)} records to GCS at {object_name}")
    dates = date_list()
    backfill_transactions(dates)

backfill_transactions_dag()

