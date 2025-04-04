{{ config(materialized='table') }}

with date_spine as (

    {{ dbt_utils.date_spine(
        start_date="'2015-01-01'",
        end_date="dateadd(day, 3650, current_date)",
        datepart="day"
    ) }}

)

select
    date_day as date,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    to_char(date_day, 'YYYY-MM') as year_month,
    trim(to_char(date_day, 'Day')) as weekday,
    extract(week from date_day) as week,
    date_trunc('week', date_day) as week_start
from date_spine
