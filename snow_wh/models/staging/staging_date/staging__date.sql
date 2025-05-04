{{ config(materialized='table') }}

with date_spine as (
    {{ dbt_utils.date_spine(
        start_date="'2015-01-01'",
        end_date="date_add(current_date, interval 3650 day)",
        datepart="day"
    ) }}
)

select
    date_day as date,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    format_date('%Y-%m', date_day) as year_month,
    trim(format_date('%A', date_day)) as weekday,
    extract(week from date_day) as week,
    date_trunc(date_day, week) as week_start
from date_spine
