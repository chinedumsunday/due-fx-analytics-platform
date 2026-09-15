{{ config(severity='warn') }}

SELECT * 
FROM {{ ref('stg_cbn_rates') }}
WHERE buy_rate > sell_rate

