select 
    corridor_code, 
    source_currency, 
    target_currency, 
    corridor_name, 
    is_active, 
    created_at
from {{ ref('stg_corridors')}}