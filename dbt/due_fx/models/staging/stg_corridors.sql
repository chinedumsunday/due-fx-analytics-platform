WITH cte AS (
    SELECT corridor_code,
    source_currency,
    target_currency,
    corridor_name,
    is_active,
    TIMESTAMP_MICROS(DIV(created_at,1000)) as created_at,
    TIMESTAMP_MICROS(DIV(updated_at,1000)) as updated_at,
    ROW_NUMBER() OVER (PARTITION BY corridor_code ORDER BY date DESC) AS row_num
    FROM {{ source('raw_fx', 'ext_corridors') }}
)

SELECT corridor_code, source_currency, target_currency, corridor_name, is_active, created_at, updated_at
FROM cte
WHERE row_num = 1
