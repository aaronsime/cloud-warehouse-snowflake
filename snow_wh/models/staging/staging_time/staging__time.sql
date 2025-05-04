{{ config(materialized='table') }}

with time_spine as (
    -- generate 1440 rows, one for each minute of the day
    select
        timestamp_add(timestamp("1970-01-01 00:00:00"), interval minute_offset minute) as full_timestamp
    from unnest(generate_array(0, 1439)) as minute_offset
)

select
    cast(full_timestamp as time) as time,
    extract(hour from full_timestamp) as hour,
    extract(minute from full_timestamp) as minute,
    format_timestamp('%H:%M', full_timestamp) as time_label,
    case
        when extract(hour from full_timestamp) between 6 and 11 then 'morning'
        when extract(hour from full_timestamp) between 12 and 17 then 'afternoon'
        when extract(hour from full_timestamp) between 18 and 21 then 'evening'
        else 'night'
    end as time_of_day
from time_spine
