# Project Charter: Due Data Platform

## Company Overview

**Due** is a Nigerian remittance startup opening up the Nigerian market to the world and vice versa, by allowing Nigerians access to global currencies. Due is a 6-month-old, angel investor-stage startup processing approximately **3 billion naira** in monthly transaction volume.

**Leadership:**
- **CEO:** Dr. Tobiloba Ojo
- **Head of Operations:** Dr. Chimedum
- **Director of Pricing:** Dr. Adaeze 

This charter defines the scope, success criteria, and constraints for Due's first internal data platform. The platform will enable daily-refreshed visibility into FX market conditions, corridor-level transaction patterns, and liquidity positioning, supporting pricing, operations, and executive decision-making. Initial deployment targets Q2 with a monthly infrastructure budget of $50 and a three-stakeholder user base.

---

## Problem Statement

Currently, pricing is done by mirroring the general market rate — ignoring that most market pricing is driven by the out-of-market rate (black market rate). This spread directly impacts the business and is, on most occasions, not responsive to the current market state until end of day.

Due to the lag in pricing:
- The business has experienced suppressed margin as suboptimal spreads erode per-transaction profit
- Market rates are often not readily available when needed, forcing the Director of Pricing to rely on assumptions and guesswork when setting prices for a given time period
- **Loss of profit** from suboptimal spread management resulting in an estimated 3-5% of the gross margin based on observed spread
- **Customer churn** — customers want their funds readily exchangeable on demand, but the lapse in pricing results in users moving to competitors with a tighter spread.

---

## Why Now

Building this data platform is urgent for the following reasons:

1. **Transaction volume growth** — the volume of transactions per second is growing, making the current manual pricing mechanics no longer feasible. Physically setting prices cannot scale with the frequency of required price adjustments.
2. **Competitive pressure** — competitors are already finding better ways to manage dynamic pricing strategically.
3. **Market timing** — Nigerian remittance volume grew ~40% year-over-year in the past two years, driven by diaspora inflows and CBN policy shifts on FX windows. Competitors with data-driven pricing are capturing disproportionate share. Due's next funding round is contingent on demonstrating operational maturity, for which analytics infrastructure is table stakes.


---
## In Scope
 - Daily batch ingestion pipelines for three data sources: CBN official FX rates, parallel market rates, and internal transaction data 
 - Cloud data warehouse with dimensional modeling (dbt on BigQuery)
 - Three role-specific dashboards: Executive, Pricing, Operations
 - Data quality monitoring and pipeline observability
 - Alerting and runbooks for common failure modes


 ## Out of Scope

| Feature | Decision | Rationale |
|---|---|---|
| Real-time data streaming | **No** | Batch processing is sufficient and more stable for current business decisions. Streaming costs do not justify the value when business needs are achievable with the stated infrastructure. |
| ML-based rate forecasting | **No** | A basic rule-based pricing mechanism backed by quality data sources is highly feasible and sufficient for current needs. |

## User Personas

### Dr. Tobiloba Ojo — CEO
Primary decision: Strategic direction, capital allocation, investor reporting
Technical ability: Reads dashboards, does not write SQL
Must answer: "What's our transaction volume and gross margin trend over the last 30 days, and which corridor is driving growth?"

### Dr. Chimedum — Head of Operations
Primary decision: Liquidity positioning, corridor health monitoring, incident response
Technical ability: Comfortable with pivot tables and dashboard filters; occasional ad-hoc SQL
Must answer: "Which corridors are experiencing elevated failure rates today, and do we have sufficient USD float for projected weekly outflows?"

### Dr. Adaeze — Director of Pricing
Primary decision: Daily spread-setting per corridor
Technical ability: Writes SQL, builds her own Metabase questions
Must answer: "What's the current gap between our applied rate, the CBN official rate, and the parallel market rate for each active corridor?"

## Success Criteria

### Performance

| Metric | Target |
|---|---|
| Executive dashboard load time | < 3 seconds |
| Executive dashboard cached | < 1 second |

### Service Level Agreements (SLA)

| Data Source | Max Staleness | Justification |
|---|---|---|
| CBN Official Rates | ≤ 24 hours | CBN publishes once daily; higher frequency adds no signal |
| Parallel Market Rates | ≤2 hours | Spreads move intraday; this is the platform's highest value signal  |
| Transaction Data | ≤2 hours | Operations team monitors failure patterns and needs near-current data |

> Data freshness is critical — we need updated in-market and out-of-market price feeds to manage the spread efficiently and maintain balanced pricing for Due and its customers. Data exceeding the thresholds above is considered stale and should trigger a pipeline alert.

### Reliability

| Metric | Target |
|---|---|
| Pipeline daily success rate | ≥ 99% successful runs over rolling 30 day window |
| Pipeline failure detection | < 15 minutes from failure to alert |
| Mean time to recovery | < 4 hours during business hours |



### Cost

| Item | Budget |
|---|---|
| Monthly infrastructure spend | $50 / month |

---

## Assumptions & Risks

### Assumptions

- Daily batch refresh is sufficient for all stated business questions
- Transaction volume remains within ~500K rows/day; 10x growth requires architectural review
- CBN API and parallel market sources remain accessible and parseable
- Stakeholders accept dbt model documentation as single source of truth for metric definitions

### Risks

- Parallel market scraping may be rate-limited or blocked (mitigation: user-agent rotation, exponential backoff, fallback to alternate aggregator)
- Service account keys stored locally during development are a credential risk (mitigation: migrate to GCP Secret Manager before any external demo)
- BigQuery query costs can spike from unbounded queries (mitigation: per-user query cost limits, mandatory partition filters on large tables)
- Single-region deployment means regional outage halts the pipeline (acknowledged — DR is out of scope at current stage)



