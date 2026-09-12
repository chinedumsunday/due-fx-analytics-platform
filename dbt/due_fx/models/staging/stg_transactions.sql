WITH cte AS (
    SELECT transaction_id, user_id, corridor_code, amount_ngn, amount_target_currency, fx_rate_applied, fee_amount_ngn, status, TIMESTAMP_MICROS(DIV(created_at, 1000)) AS created_at, TIMESTAMP_MICROS(DIV(updated_at, 1000)) AS updated_at, date,
           ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY updated_at DESC, date DESC) AS row_num
    FROM {{ source('raw_fx', 'ext_transactions') }}
)

SELECT transaction_id, user_id, corridor_code, amount_ngn, amount_target_currency, fx_rate_applied, fee_amount_ngn, status, created_at, updated_at
FROM cte
WHERE row_num = 1
