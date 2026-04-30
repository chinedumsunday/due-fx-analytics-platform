# Data Model — Due FX Analytics Platform

This document defines the dimensional model for the Due FX Analytics warehouse. The design follows a Kimball-style star schema with two fact tables (transactions and FX rates) sharing conformed dimensions for date and corridor, supporting analytical queries from three user personas (Pricing, Operations, Executive).

## 1. Business Questions
**Pricing (Dr. Adaeze):**
* What's the current gap between our applied rate, the CBN official rate, and the parallel market rate for each active corridor?
* What was the average daily spread between CBN and parallel market for NGN/USD over the last 30 days?
* What's the daily NGN/USD parallel rate trend over the last 90 days?

**Operations (Dr. Chimedum):**
* Which corridors are experiencing elevated failure rates today, and do we have sufficient USD float for projected weekly outflows?
* What's our transaction volume by corridor for the last 7 days?
* Which hour of the day has peak transaction volume, by corridor?

**Executive (Dr. Tobiloba):**
* What's our transaction volume and gross margin trend over the last 30 days, and which corridor is driving growth?
* What's our fee revenue by corridor and month over the last 6 months?

## 2. Dimensional Model - Fact Tables

### `fact_transaction`

**Grain:** Each row represents one remittance transaction created in the operational system.

**Foreign keys:**
- `user_sk` → `dim_user`
- `corridor_sk` → `dim_corridor`
- `created_date_sk` → `dim_date`

**Measures:**
- `amount_ngn` — transaction amount in NGN
- `amount_target_currency` — transaction amount in destination currency (USD/GBP/EUR)
- `fx_rate_applied` — the rate Due actually applied
- `fee_amount_ngn` — fee charged

**Other attributes:**
- `transaction_id` (degenerate dimension — preserves natural key from source)
- `transaction_status` — initiated / processing / completed / failed
- `created_at` — timestamp

**Partitioning:** partitioned by `created_date` (daily). Clustered by `corridor_sk`.

### `fact_fx_rate`

**Grain:** Grain: Each row represents one rate observation — every CBN publish and every parallel market scrape inserts a row.

**Foreign Keys:** 
- `corridor_sk` → `dim_corridor`
- `rate_source_sk` → `dim_rate_source`
- `observed_date_sk` → `dim_date`

**Measures:**
- `buy_rate` - current market buy rate
- `sell_rate` - current market sell rate 
- `mid_rate` - aggregate rate from the buy and sell rate 

**Other Attributes:**
- `observed_at` - timestamp degenerate dimension 
- `is_official` - boolean

**Partition by:** partitioned by `observed_date`

## 3. Dimension Tables

### `dim_user`

**Grain:** One row per user 

**Surrogate Key:** `user_sk`

**Natural Key:** `user_id`

**Attributes:** `user_tier` (values: standard / premium), `country`, `signup_date`, `is_current`, `valid_from`, `valid_to`

**SCD:** Type 2 — tracks tier changes, so we can ask "what tier was this user when they made this transaction?"

### `dim_corridor`

**Grain:** one row per corridor.

**Surrogate Key:** `corridor_sk`

**Natural Key:** `corridor_code`

**Attributes:** `source_currency`, `target_currency`, `corridor_name`, `is_active`

**SCD:** Type 1 — corridors don't have meaningful history; just deactivate when no longer offered.

### `dim_date`

**Grain:** one row per calendar day

**Surrogate Key:** `date_sk` 

**Natural Key:** `date_actual`

**Attributes:** `day_of_week`, `day_name`, `is_weekend`, `month`, `month_name`, `quarter`, `year`, `is_nigerian_holiday`

**Notes:** Pre-populated for ~10 years (2020-2030) so that joins always succeed for historical and near-future dates.

**SCD:** None

### `dim_rate_source`

**Grain:** one row per rate source 

**Surrogate Key:** `source_sk`

**Natural Key:** `source_code` ("CBN", "PARALLEL")

**Attributes:** `"source_name"`, `source_type`(official/unofficial), `is_active`

**SCD:** Type 1 (rate sources don't change identity)

## 4. ERD - Entity Relationship Diagram
*Star schema with two fact tables (`fact_transaction`, `fact_fx_rate`) sharing two conformed dimensions (`dim_date`, `dim_corridor`).*
```


                        ┌──────────────┐
                        │   dim_date   │
                        └──────┬───────┘
                               │ date_sk
                               │
       ┌──────────────┐    ┌───┴────────────────┐    ┌──────────────────┐
       │  dim_user    ├────┤  fact_transaction  ├────┤  dim_corridor    │
       └──────────────┘    └────────────────────┘    └──────────────────┘
                                                             │
                                                             │ corridor_sk
                                                             │
                        ┌──────────────────┐    ┌────────────┴───────┐
                        │ dim_rate_source  ├────┤   fact_fx_rate     │
                        └──────────────────┘    └────────────────────┘
                                                             │
                                                             │ date_sk
                                                             │
                                                       ┌─────┴────┐
                                                       │ dim_date │
                                                       └──────────┘

```
*Note: The two `dim_date` boxes represent the same conformed dimension table - drawn twice for visual clarity.*

## 5. Modeling Decisions and Conventions

**Naming Conventions**
- `dim_*` for dimension tables, `fact_*` for fact tables, `mart_*` for aggregate tables.
- Surrogate keys end in `_sk`, while natural keys end in `_id` or a descriptive name.
- Snake_case throughout 

**Grain choices:**
- grain for `fact_transaction` is set so that each row represents one remittance transaction created in the system.
- grain for `fact_fx_rate` one row per rate observation preserves all detail; aggregations happen in marts, not facts.

**SCD Strategy:**
- Type 2 only for `dim_user` because user tier changes matter for analyzing pricing decisions historically
- Type 1 elsewhere 

**Aggregate Marts:**
- one row per corridor per date with rolled up measures would be built as `mart_corridor_daily` to help dashboard performance, in addition to the raw facts, This is for the executive dashboard — pre-aggregating prevents scanning millions of fact rows on every dashboard load.

**Things deferred:**
- bridging tables for many to many, transaction status history fact (one row per status change), late arriving dimensions handling. These will be considered as the system scales — late-arriving dimensions, in particular, become relevant once we move to CDC ingestion.

## 6. Validation Against Business Questions

A quick check that the model actually supports the questions in Section 1:

**"What was the average daily spread between CBN and parallel market for NGN/USD over the last 30 days?"**
→ Filter `fact_fx_rate` by `corridor_sk` (NGN_USD) and date range. Pivot on `dim_rate_source` to get CBN vs parallel rates side by side per day. Compute the difference, average over 30 days.

**"What's our transaction volume by corridor for the last 7 days?"**
→ Filter `fact_transaction` by `dim_date` (last 7 days), join to `dim_corridor`, group by corridor_name, count transactions or sum `amount_ngn`.

**"Which hour of day has peak transaction volume, by corridor?"**
→ Filter `fact_transaction`, extract hour from `created_at` (the timestamp degenerate dimension), join to `dim_corridor`, group by (corridor, hour), count transactions.

If any business question can't be answered with the current model, the model needs revision before implementation.