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
    select
        location_id,
        zip_code_prefix,
        city,
        state
    from (
        select
            location_id,
            zip_code_prefix,
            city,
            state,
            -- Deduplicate based on the join keys for geo (zip_code_prefix, city).
            -- Prefer a business-meaningful timestamp from staging__geo if available (e.g., created_at DESC, updated_at DESC) as per business rules.
            -- Lacking that, use location_id ASC for deterministic selection to ensure a consistent location_id is chosen.
            ROW_NUMBER() OVER (PARTITION BY zip_code_prefix, city ORDER BY location_id ASC) as rn
        from {{ ref('staging__geo') }}
    ) deduped_geo
    where deduped_geo.rn = 1
