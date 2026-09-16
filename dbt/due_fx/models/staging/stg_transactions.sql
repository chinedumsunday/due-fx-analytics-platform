with cte as (
    select
        transaction_id,
        user_id,
        corridor_code,
        amount_ngn,
        amount_target_currency,
        fx_rate_applied,
        fee_amount_ngn,
        status,
        TIMESTAMP_MICROS(DIV(created_at, 1000)) as created_at,
        TIMESTAMP_MICROS(DIV(updated_at, 1000)) as updated_at,
        date,
        ROW_NUMBER()
            over (
                partition by transaction_id order by updated_at desc, date desc
            )
            as row_num
    from {{ source('raw_fx', 'ext_transactions') }}
)

select
    transaction_id,
    user_id,
    corridor_code,
    amount_ngn,
    amount_target_currency,
    fx_rate_applied,
    fee_amount_ngn,
    status,
    created_at,
    updated_at
from cte
where row_num = 1
