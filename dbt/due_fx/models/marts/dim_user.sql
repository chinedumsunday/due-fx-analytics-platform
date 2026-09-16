select
    user_id,
    tier,
    country,
    signup_date
from {{ ref('stg_users') }}
