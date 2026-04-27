# Architecture — Due FX Analytics Platform

## 1. Overview
The Due FX Analytics Platform is a daily-batch data system for a Nigerian remittance startup, built on Google Cloud Platform under a $50/month budget. it ingests official CBN rates, intraday parallel market data, and internal transaction logs into a centralized BigQuery warehouse. By refreshing parallel market rates every two hours, the platform gives the Director of Pricing, the Head of Operations, and the CEO a single place where they can see how Due's pricing compares to the market - replacing  the daily guesswork they currently rely on.

## 2. Architecture Diagram

![Architecture](architecture.png)
*Figure 1: End-to-end data flow showing sources, ingestion DAGs, GCS landing zone, BigQuery storage with dbt transformations orchestrated via ExternalTaskSensors, Metabase serving, and the observability stack.*

---

## 3. Component

### 3.1 Apache Airflow (Orchestration)
**What:** Apache Airflow, the industry standard tool for orchestrating data pipelines, managing the 2hr window automation for parallel market rate, 24hr window for the official rates and also the postgres database. 
**Why this:** Airflow lets me run the three ingestion DAGs on independent schedules, then use ExternalTaskSensors in master orchestration_dag to wait for all three to complete before triggering the dbt task.
**Rejected:** Cron jobs can't handle cross-task dependencies. Each scheduled job would run blindly on its own without any way to wait on the others, which means dbt would sometimes run against incomplete data.

### 3.2 Google Cloud Storage (Raw Landing Zone)
**What:** A staging area for raw data from the three sources: JSON from the CBN API, HTML + JSON (raw + parsed) from the parallel market scraper, and Parquet from the Postgres extractor. 
**Why:** this would help with maintaining the already gotten data, if for any reason there is a change in the source layout, so that way we don't lose any data when there is a failure, if the parallel market site changes its HTML layout, my parser will break but the raw HTML is already saved in GCS, so i can fix the parser and reprocess without re-scraping.
**Rejected:** moving data into directly into bigquery, would work but not the best since we wont have a fall back for when something fails or isn't parsed correctly 

### 3.3 BigQuery (Warehouse)
**What:** BigQuery is a fully managed, serverless and also highly scalable cloud data warehouse made by Google cloud for fast SQL based analysis for large datasets. 
**Why:** BigQuery's free tier (10GB storage, 1TB queries per month) covers the entire $50 budget, if I use partition filters on large queries. it scales fine to the 500k rows/day target without architectural change. 
**Rejected:** Snowflake would also work, but the free trial expires after 30 days, after that the project would stop running. BigQuery's permanent free tier means I can keep this portfolio project live for free.

### 3.4 dbt (Transformation)
**What:** A tool that enables engineers transform data in warehouse using SQL with version control support and more
**Why:** dbt gives me three things i actually need: 
1. version-controlled SQL transformatiosn so i can review changes in PRs.
2. a built-in testing framework so i can assert things like 'fx_rate must be > 0' on every run.
3. auto-generated lineage docs so i can see how marts depend on staging models.
**Rejected:**  an alternative would have been the BigQuery Scheduled Queries but the absence of version control and frameworks for testing, and history tracking is a condition we cannot trade in this pipeline.

### 3.5 Metabase (BI/Serving)
**What:** This would be a self hosted dashboard served to the necessary individuals.
**Why:** Metabase is free, supports BigQuery natively, and lets non-technical users (the CEO) click through pre-built dashboards while letting Dr. Adaeze (Director of Pricing) write her own SQL questions when she needs to dig deeper. That mixed-skill audience is exactly what Metabase is designed for. 
**Rejected:** Tableau would have been another alternative but the cost is a hitch as it crosses the $50 slated budget for the pipeline. 

### 3.6 Operational Postgres (Source)
**What:** A simulated PostgreSQL database modeling Due's operational transaction system. A data generator continuously inserts realistic transactions to mimic a live remittance environment.
**Why:**Pulling from a live operational database via incremental SQL extraction is the most common ingestion pattern in real DE work. Building it here means I can talk fluently about watermarks, idempotency, and clock skew in interviews — and I'll reuse this same database for the CDC project later.
**Rejected:** CSVs would not solve the problem of timing and integrity. 

### 3.7 Observability Stack (Cloud Monitoring + Grafana + Telegram)
**What:** This is a system for monitoring the pipeline on the cloud and getting alerts in times when the conditions require it. 
**Why:** The 15-minute failure detection SLA needs push notifications, not email. Telegram is free, has a simple bot API, and matches the same alerting pattern I used in the MTL News Desk pipeline — so I'm reusing knowledge instead of learning a new tool. Cloud Monitoring is GCP-native (no setup), and Grafana Cloud's free tier stitches everything into one dashboard. 
**Rejected:** Email notifications would be too slow for monitoring this service due to the focus being with the forex market 

---

## 4. Data Flow Walkthrough: Parallel Market Update

1.  **Clock-Trigger:**  Every 2 hours during business hours (e.g., 17:00 WAT), Airflow triggers the parallel_market_dag.
2.  **Extract:** The task sends an HTTPS GET to the parallel market aggregator with rotated user-agent headers to reduce blocking risk. On 5xx response or timeout, it retries with exponential backoff up to 3 times before failing the task. 
3.  **Land raw HTML**: The raw HTML is saved to gs://due-fx-data/raw/parallel_market/date=YYYY-MM-DD/hour=HH/page.html. Saving the raw response before parsing means a parser fix later doesn't require re-scraping the source.
4.  **Parse & Convert:** A separate task reads the saved HTML, extracts the rate table, and writes parsed records as JSON back to the same GCS prefix.
5.  **Schema Check:** The parsed data is validated — rate must be a positive float, timestamp must be present. If validation fails, the task fails and triggers an alert.
6.  **Orchestration Sensor:** The orchestration_dag running its ExternalTaskSensor detects that all three ingestion DAGs have completed successfully.
7.  **dbt Build:** `dbt build` runs. It creates a new `stg_parallel_rates` table, casting strings to decimals and removing any duplicates.
8.  **Checking the spread:** dbt joins the parallel rate with the official CBN rate to create the `fact_fx_spread` mart.
9.  **Visual Update:** Metabase’s BigQuery connection refreshes. Dr. Adaeze sees the updated spread and adjusts the corridor pricing accordingly.
10. **Feedback Loop:** If any step exceeds 15 minutes or fails, a Telegram bot pings the team with a link to the specific failing Airflow task log.

---

## 5. Architecture Decision Records (ADRs)

### ADR-001: Two-stage "raw + parse" pattern for scrapers
**Context:** Parallel market sites are unstable. If we parse during extraction and the site changes, we lose the data.
**Decision:** Always land raw HTML in GCS before parsing into JSON or Parquet.
**Consequences:** 
* **High Recovery:** We can fix parsers and "re-ingest" history without re-scraping from the source website.
* **Storage:** Minor increase in GCS costs, handled by a 90-day retention policy.


### ADR-002: External tables for Raw, Native for Staging/Marts
**Context:** We need a balance between cost-effective ingestion and very responsive dashboards 
**Decision:** Keep raw data as BigQuery external tables pointing at GCS; materialize staging and marts as native BigQuery tables. 
**Consequences:** 
*  **Performance:** Executive dashboards load in under 3 seconds because they query optimized native storage with partition pruning.
* **Cost:** No BigQuery storage fees for raw data since it lives in GCS.

---

## 6. Out of Scope (and Why That's Acceptable)

* **Real-time Streaming:** All sources update on hour-or-longer cadences, and no business question identified in the charter requires sub-hour freshness. A streaming stack like Kafka + Flink would also blow the $50 budget.
* **ML Forecasting:** A rule-based spread (e.g., parallel rate + fixed margin) is more transparent and reliable for a seed-stage startup than an unproven model. Worth revisiting at Series A. 
* **Row-Level Security:** With only three users, managing complex IAM/RLS for different departments is deferred until the team scales.
* **No multi-region failover**. The platform runs in us-central1 only. A regional outage halts the pipeline. Acceptable at current stage — RTO of 24 hours fits a seed-stage company.

---

## 7. Evolution Path

At 10x transaction volume (~5M rows/day), the watermark-based Postgres extraction becomes the first bottleneck — full incremental scans every two hours start putting pressure on the operational database. The fix is replacing the SQL extractor with a CDC pipeline using Debezium reading the Postgres write-ahead log into Kafka, then sinking into the same BigQuery staging layer. This drops transaction data staleness from 2 hours to sub-minute without hammering the source DB.

At Series A, the platform adds team-scale concerns: deeper data quality checks (Great Expectations or Soda), column-level lineage across tools (OpenLineage), and a semantic layer (Cube or dbt Semantic Layer) once analyst headcount exceeds five — at that point, metric drift across dashboards becomes a real risk. Metabase moves to a managed deployment to handle the larger internal analyst team.