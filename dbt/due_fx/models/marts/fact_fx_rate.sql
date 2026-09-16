with cbn as (
    select
        c.ratedate as rate_date,
        case
            when TRIM(c.currency) = "US DOLLAR" then "USD"
            when TRIM(c.currency) = "POUNDS STERLING" then "GBP"
            when TRIM(c.currency) = "POUND STERLING" then "GBP"
            when TRIM(c.currency) = "EURO" then "EUR"
            when TRIM(c.currency) = "UAE DIRHAM" then "AED"
        end as currency_code,
        "CBN" as source_code,
        c.buy_rate,
        c.sell_rate,
        c.mid_rate
    from {{ ref('stg_cbn_rates') }} as c
),

parallel as (
    select
        p.history_date as rate_date,
        p.code as currency_code,
        "ABOKIDOLLAR" as source_code,
        p.buy_rate,
        p.sell_rate,
        CAST(NULL as FLOAT64) as mid_rate
    from {{ ref('stg_parallel_rates') }} as p
)

select *
from cbn
where currency_code is not NULL
union all
select *
from parallel
where currency_code in ("USD", "GBP", "EUR", "AED")
