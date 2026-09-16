with cte as (
    select
        id,
        currency,
        ratedate,
        buyingrate,
        sellingrate,
        centralrate,
        date,
        ROW_NUMBER()
            over (partition by currency, ratedate order by date desc, id desc)
            as row_num
    from {{ source('raw_fx', 'ext_cbn_rates') }}
)

select
    id,
    currency,
    ratedate,
    buyingrate as buy_rate,
    sellingrate as sell_rate,
    centralrate as mid_rate,
    date
from cte
where row_num = 1
