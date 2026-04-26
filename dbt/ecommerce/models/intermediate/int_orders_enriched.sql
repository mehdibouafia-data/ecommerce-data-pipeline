with carts as (
    select * from {{ ref('stg_carts') }}
),

cart_items as (
    select * from {{ ref('stg_cart_items') }}
),

products as (
    select * from {{ ref('stg_products') }}
)


select
     -- identifiers
     ci.cart_id,
     ci.product_id,
     c.user_id,

     -- product
     ci.product_name,
     p.category,
     p.brand,
     p.rating,
     p.stock,

     -- prices & quantities
     ci.quantity,
     ci.price                     as unit_price,
     ci.total                     as item_total,
     ci.discount_percentage,
     ci.discounted_total          as item_discounted_total,

     -- cart
     c.total                      as cart_total,
     c.discounted_total           as cart_discounted_total,

     -- metadata
     ci.ingested_at

from cart_items ci
inner join carts c
     on ci.cart_id = c.cart_id
inner join products p
     on ci.product_id = p.product_id