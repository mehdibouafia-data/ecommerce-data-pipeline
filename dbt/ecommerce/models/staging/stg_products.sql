with source as (
    select * from {{ source('raw', 'products') }}
    where id is not null
      and title is not null
      and price is not null
      and category is not null
)

select
    id                                          as product_id,
    title                                       as product_name,
    price::numeric(10, 2)                       as price,
    category,
    stock::integer                              as stock,
    brand,
    rating::numeric(3, 2)                       as rating,
    discount_percentage::numeric(5, 2)          as discount_percentage,
    ingested_at
from source
