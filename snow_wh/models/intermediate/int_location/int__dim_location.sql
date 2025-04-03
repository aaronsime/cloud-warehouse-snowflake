with dim_location as (
    select
        zip_code_prefix,
        city,
        state,
        country
    from {{ ref('staging__geo') }}
)
select *
from dim_location
