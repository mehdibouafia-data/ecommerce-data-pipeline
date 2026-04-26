with source as (
    select * from {{ source('raw', 'cart_items') }}
    where cart_id is not null
      and product_id is not null
      and quantity is not null
)

select
    cart_id,
    product_id,
    title                               as product_name,
    price::numeric(10, 2)               as price,
    quantity::integer                   as quantity,
    total::numeric(10, 2)               as total,
    discount_percentage::numeric(5, 2)  as discount_percentage,
    discounted_total::numeric(10, 2)    as discounted_total,
    ingested_at
from source