with cte as (
    select
        user_id,
        tier,
        country,
        signup_date,
        TIMESTAMP_MICROS(DIV(created_at, 1000)) as created_at,
        TIMESTAMP_MICROS(DIV(updated_at, 1000)) as updated_at,
        ROW_NUMBER() over (partition by user_id order by date desc) as row_num
    from {{ source('raw_fx', 'ext_users') }}
)

select
    user_id,
    tier,
    country,
    signup_date,
    created_at,
    updated_at
from cte
where row_num = 1
