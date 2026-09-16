# Runbook

## Starting the stack

Order matters — the Postgres stack owns the Docker network.

    cd Due && docker compose up -d
    cd airflow && docker compose up -d
    cd metabase && docker compose up -d

## Common failures

### "external network due-network not found"
The Postgres stack isn't running. Start it first.

### Extraction DAG finds zero rows
Check the live generator is running:
    ps aux | grep generate.py
If absent: `python data-generator/generate.py --live`

### dbt tests fail on stg_cbn_rates buy/sell
Expected. See ADR-011 — CBN publishes ~35 rows with inverted rates. The test
is set to warn.

### Source freshness warns on ext_cbn_rates
Expected. `ratedate` is a DATE, so its max reads as midnight — up to 24 hours
staler than reality.

### Metabase dashboards show no recent data
Check the transform DAG ran:
    [link to Airflow UI]

## Regenerating data

Full reset (destroys all transactions):
    python data-generator/generate.py

Live mode (appends):
    python data-generator/generate.py --live

## Rebuilding the warehouse

    cd dbt/due_fx
    dbt deps && dbt seed && dbt build

## Cost monitoring

Budget alert at $50/month. Check spend:
GCP Console → Billing → Reports