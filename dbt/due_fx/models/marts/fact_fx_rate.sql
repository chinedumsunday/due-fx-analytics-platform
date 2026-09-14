with cbn AS (
    SELECT
        c.ratedate as rate_date,
        CASE 
            WHEN TRIM(c.currency) = "US DOLLAR" THEN "USD"
            WHEN TRIM(c.currency) = "POUNDS STERLING" THEN "GBP"
            WHEN TRIM(c.currency) = "POUND STERLING" THEN "GBP"
            WHEN TRIM(c.currency) = "EURO" THEN "EUR"
            WHEN TRIM(c.currency) = "UAE DIRHAM" THEN "AED"
        END AS currency_code,
        "CBN" as source_code,
        c.buy_rate as buy_rate,
        c.sell_rate as sell_rate,
        c.mid_rate as mid_rate
    FROM {{ref('stg_cbn_rates')}} as c
),

parallel AS (
    SELECT
        p.history_date as rate_date,
        p.code as currency_code,
        "ABOKIDOLLAR" as source_code,
        p.buy_rate as buy_rate,
        p.sell_rate as sell_rate,
        CAST(NULL AS FLOAT64) as mid_rate
    FROM {{ref('stg_parallel_rates')}} as p
)

SELECT * 
FROM cbn 
WHERE currency_code IS NOT NULL 
UNION ALL
SELECT * 
FROM parallel
WHERE currency_code IN ('USD', 'GBP','EUR','AED')