SELECT
    user_id, 
    tier, 
    country, 
    signup_date
FROM {{ ref('stg_users')}}