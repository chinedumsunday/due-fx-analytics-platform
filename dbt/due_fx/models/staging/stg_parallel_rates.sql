WITH cte AS (
    SELECT * FROM {{ source('raw_fx', 'ext_parallel_rates') }}
    WHERE type = "Black Market"
),

cte1 AS (
    SELECT
        code,
        nested_json.date AS history_date,
        nested_json.buyRate AS buy_rate,
        nested_json.sellRate AS sell_rate,
        c.date as date
    FROM cte as c,
    UNNEST(history) AS nested_json     
),

cte2 AS (
    SELECT code, history_date, buy_rate, sell_rate, date,
        ROW_NUMBER() OVER (PARTITION BY code, history_date ORDER BY date DESC) AS row_num
    FROM cte1
)


SELECT code, history_date,buy_rate, sell_rate, date
FROM cte2
WHERE row_num = 1
