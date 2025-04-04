with dim_customer as(
    select
        customer_id,
        customer_unique_id
    from {{ ref('staging__customer') }}
)
select *
from dim_customer
