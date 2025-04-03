with geo as(
    select
        "geolocation_zip_code_prefix" as zip_code_prefix,
        "geolocation_lat" as latitude,
        "geolocation_lng" as longitude,
        {{ replace_accented_chars('"geolocation_city"') }} as city,
        "geolocation_state" as state,
        'Brazil' as country,
        row_number() over (partition by "geolocation_zip_code_prefix" order by "geolocation_zip_code_prefix") as row_num
    from {{ source('raw', 'OLIST_GEOLOCATION') }}
)
select
    md5(concat(zip_code_prefix, city, state)) as location_id,
    zip_code_prefix,
    city,
    state
from geo
where row_num = 1
