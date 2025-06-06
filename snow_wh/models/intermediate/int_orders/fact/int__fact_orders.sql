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
SELECT
    g_deduped.location_id,
    g_deduped.zip_code_prefix,
    g_deduped.city,
    g_deduped.state
FROM (
    SELECT
        sg.location_id,
        sg.zip_code_prefix,
        sg.city,
        sg.state,
        -- Deduplicating geo data: Using location_id for deterministic ordering as no specific timestamp for staging__geo is provided.
        -- If a timestamp (e.g., created_at, updated_at) exists in staging__geo, it should be preferred for ordering
        -- to select the most relevant geo entry based on business rules (e.g., most recent).
        ROW_NUMBER() OVER (PARTITION BY sg.zip_code_prefix, sg.city ORDER BY sg.location_id ASC) as rn_geo
    FROM {{ ref('staging__geo') }} sg
) g_deduped
WHERE g_deduped.rn_geo = 1
