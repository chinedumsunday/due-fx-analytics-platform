# Due FX Analytics Platform

> Daily-refreshed FX market and remittance transaction analytics for a Nigerian fintech.

**Status:** 🚧 In active development — Day 1 of 11

## Overview

This repository contains the end-to-end data platform for **Due**, a simulated Nigerian remittance startup. The platform ingests foreign exchange rate data from multiple sources and internal transaction data, transforms it into a dimensional warehouse model, and serves role-specific analytics dashboards to pricing, operations, and executive stakeholders.

This project is part of a production-grade data engineering portfolio. See [docs/project-charter.md](docs/project-charter.md) for full business context.

## Architecture

![Architecture Diagram](docs/architecture.png)

*Architecture diagram coming at end of Day 1.*

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow |
| Ingestion | Python (requests, BeautifulSoup, psycopg2) |
| Storage | Google Cloud Storage (raw), BigQuery (warehouse) |
| Transformation | dbt (dbt-bigquery) |
| BI / Serving | Metabase |
| Infrastructure | GCP (Compute Engine, Cloud Storage, BigQuery, Secret Manager) |
| Observability | Cloud Monitoring, Grafana Cloud, Telegram alerts |
| CI/CD | GitHub Actions |

## Data Sources

1. **Central Bank of Nigeria (CBN)** — Official daily FX rates (REST API)
2. **Parallel Market Aggregator** — Unofficial market rates (HTML scraping)
3. **Internal Operational Database** — Simulated transaction data (PostgreSQL CDC)

## Repository Structure
.
├── docs/               # Project charter, architecture, data model, runbooks
├── airflow/            # DAGs and plugins
├── dbt/                # dbt project (staging + marts)
├── data-generator/     # Postgres transaction simulator
├── infra/              # Terraform (added in later phase)
├── scripts/            # Utility scripts
├── tests/              # Integration and pipeline tests
└── .github/workflows/  # CI/CD pipelines

## Setup

*Setup instructions will be added as components are built. Not yet runnable end-to-end.*

## Cost

Target infrastructure spend: **< $50 / month** on GCP free tier + minimal chargeable resources. Detailed cost breakdown at project completion.

## Project Documentation

- [Project Charter](docs/project-charter.md) — Scope, success criteria, constraints
- Architecture — *coming at end of Day 1*
- Data Model — *coming at end of Day 1*
- Runbook — *coming at end of Day 1*

## License

MIT — see [LICENSE](LICENSE)

## Author

Chinedum 