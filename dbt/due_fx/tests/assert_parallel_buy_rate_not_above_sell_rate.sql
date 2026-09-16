{{ config(severity='warn') }}

select *
from {{ ref('stg_parallel_rates') }}
where buy_rate > sell_rate
