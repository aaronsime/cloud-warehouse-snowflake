with orders as (
    select
	order_id as order_id,
	customer_id as customer_id,
	order_status as order_status,
	order_purchase_timestamp as order_purchase_timestamp,
	order_approved_at as order_approved_at,
	order_delivered_carrier_date as order_delivered_carrier_date,
	order_delivered_customer_date as order_delivered_customer_date,
	order_estimated_delivery_date as order_estimated_delivery_date
    from {{ source('raw', 'olist_orders') }}
)
select *
from orders
