with source as (
    select * from {{ source('raw', 'carts') }}
    where id is not null
      and user_id is not null
)

select
    id                                  as cart_id,
    user_id,
    total::numeric(10, 2)               as total,
    discounted_total::numeric(10, 2)    as discounted_total,
    ingested_at
from source
