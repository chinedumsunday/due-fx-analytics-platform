import json
import requests
import datetime
from datetime import datetime as dt
from airflow.sdk import dag, task
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.sdk import get_current_context


# from airflow.decorators import dag, task

CBN_URL = "https://www.cbn.gov.ng/api/GetAllExchangeRates?format=json"

@dag(
    dag_id = "cbn_rates_dag",
    schedule = "@daily",
    start_date = datetime.datetime(2026, 7, 1),
    catchup = False,
    tags = ["cbn", "ingestion"],
)

def cbn_rates_dag():
    @task()
    def fetch_cbn_rates():
        n_rates = []
        response = requests.get(CBN_URL, timeout=30)
        response.raise_for_status()
        for rate in response.json():
            n_rates.append(json.dumps(rate))
        rates = "\n".join(n_rates)
        return rates
    
    @task()
    def land_cbn_rates(rates):
        ctx = get_current_context()
        ds = ctx["ds"]  # Get the execution date in YYYY-MM-DD format
        hook = GCSHook(gcp_conn_id="google_cloud_default")
        object_name = f"raw/cbn/date={ds}/rates.ndjson"
        hook.upload(bucket_name="due-fx-data-245535", object_name=object_name, data=rates)
        return object_name

    @task()
    def validate_cbn_rates(object_name):
        ctx = get_current_context()
        ds = ctx["ds"]  # Get the execution date in YYYY-MM-DD format
        hook = GCSHook(gcp_conn_id="google_cloud_default")
        data = hook.download(bucket_name="due-fx-data-245535", object_name=object_name)
        data = data.decode("utf-8")
        rates = [json.loads(line) for line in data.splitlines() if line.strip()]
        assert isinstance(rates, list), "payload is not a list"
        assert len(rates) > 0, "payload is empty"
        required = {"currency", "ratedate", "centralrate"}
        assert required.issubset(rates[0].keys()), f"missing fields: {required - rates[0].keys()}"    
        dates = {r["ratedate"] for r in rates}
        latest_date = max(dt.strptime(d, "%Y-%m-%d") for d in dates)
        days_old = dt.strptime(ds, "%Y-%m-%d") - latest_date
        assert days_old.days <= 2, f"rates for {ds} are more than 2 days old"
        print(f"validated {len(rates)} records, latest date {max(dates)}")
        return {"record_count": len(rates), "latest_date": max(dates)}
    
    landed = land_cbn_rates(fetch_cbn_rates())
    validate_cbn_rates(landed)


cbn_rates_dag()
