with cte as (
    select
        corridor_code,
        source_currency,
        target_currency,
        corridor_name,
        is_active,
        TIMESTAMP_MICROS(DIV(created_at, 1000)) as created_at,
        TIMESTAMP_MICROS(DIV(updated_at, 1000)) as updated_at,
        ROW_NUMBER()
            over (partition by corridor_code order by date desc)
            as row_num
    from {{ source('raw_fx', 'ext_corridors') }}
)

select
    corridor_code,
    source_currency,
    target_currency,
    corridor_name,
    is_active,
    created_at,
    updated_at
from cte
where row_num = 1
