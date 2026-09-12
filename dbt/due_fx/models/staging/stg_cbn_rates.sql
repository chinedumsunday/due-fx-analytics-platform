WITH cte AS (
    SELECT id, currency, ratedate, buyingrate, sellingrate, centralrate, date,
           ROW_NUMBER() OVER (PARTITION BY currency, ratedate ORDER BY date DESC, id DESC) AS row_num
    FROM {{ source('raw_fx', 'ext_cbn_rates') }}
)

SELECT id, currency, ratedate, buyingrate as buy_rate, sellingrate as sell_rate, centralrate as mid_rate, date 
FROM cte
WHERE row_num = 1
