select
    transaction_id,
    user_id,
    corridor_code,
    CAST(created_at as DATE) as date_day,
    amount_ngn,
    amount_target_currency,
    fx_rate_applied,
    fee_amount_ngn,
    status
from {{ ref('stg_transactions') }}
