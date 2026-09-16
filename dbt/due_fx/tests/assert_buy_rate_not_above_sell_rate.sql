{{ config(severity='warn') }}

select *
from {{ ref('stg_cbn_rates') }}
where buy_rate > sell_rate
