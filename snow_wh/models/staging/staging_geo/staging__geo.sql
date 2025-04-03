with geo as(
    select
        "geolocation_zip_code_prefix" as zip_code_prefix,
        "geolocation_lat" as latitude,
        "geolocation_lng" as longitude,
        "geolocation_city" as city,
        "geolocation_state" as state,
        'Brazil' as country
    from {{ source('raw', 'OLIST_GEOLOCATION') }}
)
select
    md5(concat(zip_code_prefix, latitude, longitude, city, state)) as location_id,
    zip_code_prefix,
    latitude,
    longitude,
    city,
    state
from geo
