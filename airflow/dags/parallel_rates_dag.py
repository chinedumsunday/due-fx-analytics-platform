import json
import requests
import datetime
from airflow.sdk import dag, task
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.sdk import get_current_context
from datetime import datetime as dt
# import pandas as pd

keys = {"Buy Rate":"buy_rate","Sell Rate":"sell_rate","Currency Name":"currency_name","Type":"type","Code":"code","lastUpdated":"last_updated"}


PARALLEL_URL = "https://abokidollar.com/api/rates"

@dag(
    dag_id = "parallel_rates_dag",
    schedule = "0 2 * * *",
    start_date = datetime.datetime(2026, 7, 1),
    catchup = False,
    tags = ["parallel", "ingestion"],
)
def parallel_rates_dag():
    @task()
    def fetch_parallel_rates():
        n_rates = []
        response = requests.get(PARALLEL_URL, timeout=30)
        response.raise_for_status()
        for rate in response.json():
            rate = {keys.get(k, k): v for k, v in rate.items()}
            n_rates.append(json.dumps(rate))
        rates = "\n".join(n_rates)
        return rates

    @task()
    def land_parallel_rates(rates):
        ctx = get_current_context()
        ds = ctx["ds"]  # Get the execution date in YYYY-MM-DD format
        hook = GCSHook(gcp_conn_id="google_cloud_default")
        parallel_rates = f"raw/parallel/date={ds}/rates.ndjson"
        hook.upload(bucket_name="due-fx-data-245535", object_name=parallel_rates, data=rates)
        return parallel_rates

    @task()
    def validate_parallel_rates(parallel_rates):
        ctx = get_current_context()
        ds = ctx["ds"]  # Get the execution date in YYYY-MM-DD format
        hook = GCSHook(gcp_conn_id="google_cloud_default")
        data = hook.download(bucket_name="due-fx-data-245535", object_name=parallel_rates)
        data = data.decode("utf-8")
        rates = [json.loads(line) for line in data.splitlines() if line.strip()]
        black_market_rates = [rate for rate in rates if rate.get('type') == "Black Market"]
        assert isinstance(rates, list), "payload is not a list"
        assert all('type' in rate for rate in black_market_rates), "Not all rates have a Type field"
        assert all('code' in rate for rate in black_market_rates), "Not all rates have a Code field"
        assert all('buy_rate' in rate for rate in black_market_rates), "Not all rates have a Buy Rate field"
        assert all('sell_rate' in rate for rate in black_market_rates), "Not all rates have a Sell Rate field"
        assert all(rate.get('buy_rate') <= rate.get('sell_rate') for rate in black_market_rates), "Some Buy Rates are greater than Sell Rates"
        dates = {rate.get('last_updated')[0:10] for rate in black_market_rates if rate.get('last_updated')}
        days_old = dt.strptime(ds, "%Y-%m-%d") - max(dt.strptime(d, "%Y-%m-%d") for d in dates)
        assert days_old.days <= 2, f"Some rates are more than 2 days old"
        required_codes = {"USD", "EUR", "GBP", "AED"}
        assert required_codes.issubset({rate.get('code') for rate in black_market_rates}), f"Missing required codes: {required_codes - {rate.get('code') for rate in black_market_rates}}"
        assert all(rate.get('buy_rate') > 0 for rate in black_market_rates), "Some rates have non-positive Buy Rates"
        assert all(rate.get('sell_rate') > 0 for rate in black_market_rates), "Some rates have non-positive Sell Rates"
        assert all(rate.get('last_updated') is not None for rate in black_market_rates), "Some rates have missing lastUpdated field"
        print(f"validated {len(black_market_rates)} records, latest date {max(rate['last_updated'] for rate in black_market_rates)}")
        return {"record_count": len(black_market_rates), "latest_date": max(rate['last_updated'] for rate in black_market_rates)}


    landed = land_parallel_rates(fetch_parallel_rates())
    validate_parallel_rates(landed)

parallel_rates_dag()