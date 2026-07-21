import requests
import datetime
from airflow.sdk import dag, task
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
        response = requests.get(CBN_URL, timeout=30)
        response.raise_for_status()
        rates = response.json()
        print(f"Fetched {rates[0]} CBN rates")
        return len(rates)
        
        
    fetch_cbn_rates()


cbn_rates_dag()
