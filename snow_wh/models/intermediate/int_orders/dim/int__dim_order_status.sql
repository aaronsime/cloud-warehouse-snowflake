with order_status as (
    select
        distinct order_status,
    from {{ ref('staging__orders') }}
)
select
    md5(order_status) as order_status_id,
    order_status
from order_status
