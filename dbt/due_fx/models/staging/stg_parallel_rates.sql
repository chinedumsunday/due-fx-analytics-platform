with cte as (
    select * from {{ source('raw_fx', 'ext_parallel_rates') }}
    where type = "Black Market"
),

cte1 as (
    select
        code,
        nested_json.date as history_date,
        nested_json.buyrate as buy_rate,
        nested_json.sellrate as sell_rate,
        c.date
    from cte as c,
        UNNEST(history) as nested_json
),

cte2 as (
    select
        code,
        history_date,
        buy_rate,
        sell_rate,
        date,
        ROW_NUMBER()
            over (partition by code, history_date order by date desc)
            as row_num
    from cte1
)


select
    code,
    history_date,
    buy_rate,
    sell_rate,
    date
from cte2
where row_num = 1
