SELECT
    date_day as txn_date,
    corridor_code,
    count(transaction_id) as num_of_transactions,
    sum(amount_ngn) as trn_vol_naira,
    sum(fee_amount_ngn) as total_fees,
    avg(amount_ngn) as avg_trn_size,
    sum(case when status = "completed" then 1 else 0 end ) * 1.0 / NULLIF(sum(case when status in ("completed", "failed") then 1 else 0 end), 0) as success_rate,
    countif(status = "completed") as completed_txn,
    countif(status = "failed") as failed_txn
FROM {{ref('fact_transaction')}}
GROUP BY txn_date, corridor_code