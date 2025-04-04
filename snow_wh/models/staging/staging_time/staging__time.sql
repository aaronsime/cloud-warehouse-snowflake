{{ config(materialized='table') }}

with time_spine as (
    -- Generate 1440 rows, one for each minute of the day
    select
        dateadd(minute, seq4(), to_timestamp_ltz('1970-01-01 00:00:00')) as full_timestamp
    from table(generator(rowcount => 1440))
)

select
    full_timestamp::time as time,
    extract(hour from full_timestamp) as hour,
    extract(minute from full_timestamp) as minute,
    to_char(full_timestamp, 'HH24:MI') as time_label,
    case
        when extract(hour from full_timestamp) between 6 and 11 then 'Morning'
        when extract(hour from full_timestamp) between 12 and 17 then 'Afternoon'
        when extract(hour from full_timestamp) between 18 and 21 then 'Evening'
        else 'Night'
    end as time_of_day
from time_spine
