with stage_customer as (
    select
        customer_id as customer_id,
        customer_unique_id as customer_unique_id,
        customer_zip_code_prefix as customer_zip_code_prefix,
        {{ replace_accented_chars('customer_city') }} as customer_city,
        customer_state as customer_state
    from {{ source('raw', 'olist_customers') }}
)
select
    *
from stage_customer
