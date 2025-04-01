with stage_customer as (
    select
        "customer_id" as customer_id,
        "customer_unique_id" as customer_unique_id,
        "customer_zip_code_prefix" as customer_zip_code_prefix,
        "customer_city" as customer_city,
        "customer_state" as customer_state
    from {{ source('raw', 'OLIST_CUSTOMERS') }}
)
select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
from stage_customer
