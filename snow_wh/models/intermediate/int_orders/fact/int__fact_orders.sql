with customer as(
    select
        customer_id,
        customer_city,
        customer_state,
        customer_zip_code_prefix
    from {{ ref('staging__customer') }}
),

geo as(
    select
        location_id,
        zip_code_prefix,
        city,
        state
    from {{ ref('staging__geo') }}
    -- Deduplicate geo data: A single zip_code_prefix and city can sometimes map to multiple location_ids.
    -- To ensure a unique location for each customer's city and zip prefix, we select one deterministically.
    -- Here, we pick the location with the smallest location_id as per deterministic ordering when no timestamp is available.
    -- This resolves potential fan-out issues when joining customers to geographic locations, addressing the root cause of order_id duplication.
    qualify row_number() over (partition by zip_code_prefix, city order by location_id asc) = 1
),

orders as (
    select
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date
    from {{ ref('staging__orders') }}
),

order_status as (
    select
        order_status_id,
        order_status
    from {{ ref('int__dim_order_status') }}
)

select
    o.order_id,
    o.customer_id,
    g.location_id,
    os.order_status_id,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date
from orders o
left join customer c
    on o.customer_id = c.customer_id
left join order_status os
    on o.order_status = os.order_status
left join geo g
    on c.customer_zip_code_prefix = g.zip_code_prefix
    and c.customer_city = g.city
