with dim_location_cte as (
    select
        location_id,
        zip_code_prefix,
        city,
        state
    from {{ ref('staging__geo') }}
)
select *
from dim_location_cte
