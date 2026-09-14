WITH cte AS (
    SELECT user_id,
    tier,
    country, 
    signup_date,
    TIMESTAMP_MICROS(DIV(created_at,1000)) as created_at,
    TIMESTAMP_MICROS(DIV(updated_at,1000)) as updated_at,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY date DESC) AS row_num
    FROM {{ source('raw_fx', 'ext_users') }}
)

SELECT user_id, tier, country, signup_date, created_at, updated_at
FROM cte
WHERE row_num = 1
