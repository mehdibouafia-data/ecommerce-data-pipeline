with users as (
    select * from {{ ref('stg_users') }}
),

carts as (
    select * from {{ ref('stg_carts') }}
)


select
    -- customer
    u.user_id,
    u.first_name,
    u.last_name,
    u.email,
    u.age,
    u.city,
    u.country,
    u.company_name,

    -- order
    c.cart_id,
    c.total                     as cart_total,
    c.discounted_total          as cart_discounted_total,

    -- metadata
    c.ingested_at

from users u
inner join carts c
    on u.user_id = c.user_id
