{{ config(severity='warn') }}

SELECT * 
FROM {{ ref('stg_parallel_rates') }}
WHERE buy_rate > sell_rate

