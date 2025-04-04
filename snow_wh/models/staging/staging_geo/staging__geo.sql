with geo as(
    select
        "geolocation_zip_code_prefix" as zip_code_prefix,
        "geolocation_lat" as latitude,
        "geolocation_lng" as longitude,
        {{ replace_accented_chars('"geolocation_city"') }} as city,
        "geolocation_state" as state
    from {{ source('raw', 'OLIST_GEOLOCATION') }}
),

customer_location as (
    select
        customer_zip_code_prefix as zip_code_prefix,
        {{ replace_accented_chars('customer_city') }} as city,
        customer_state as state
    from {{ ref('staging__customer') }}
),

union_geo as (
    select
        zip_code_prefix,
        city,
        state
    from geo
    union
    select
        zip_code_prefix,
        city,
        state
    from customer_location
)
select
    md5(concat(zip_code_prefix, city, state)) as location_id,
    zip_code_prefix,
    city,
    state
from union_geo
