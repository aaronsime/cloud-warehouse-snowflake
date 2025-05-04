with order_status_cte as (
    select distinct
        order_status
    from {{ ref('staging__orders') }}
)

select
    to_hex(md5(order_status)) as order_status_id,
    order_status
from order_status_cte
