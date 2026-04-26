with orders as (
    select * from {{ ref('int_orders_enriched') }}
),

-- Pre-aggregation of revenue by category for ranking
category_revenue as (
    select
        category,
        product_id,
        sum(item_discounted_total)      as product_revenue_in_category
    from orders
    group by category, product_id
)

select
    -- identifiers
    o.cart_id,
    o.product_id,
    o.user_id,

    -- product
    o.product_name,
    o.category,
    o.brand,
    o.rating,
    o.stock,

    -- sales
    o.quantity,
    o.unit_price,
    o.discount_percentage,
    o.item_total,
    o.item_discounted_total,

    -- cart
    o.cart_total,
    o.cart_discounted_total,

    -- % contribution of the item to the cart
    round(
        SAFE_DIVIDE(
            o.item_discounted_total,
            o.cart_discounted_total
        ),
        4
    )   as pct_of_cart,

    -- revenue quartile per item (1 = top 25%)
    ntile(4) over (
        order by o.item_discounted_total desc
    )    as revenue_quartile,

    -- ranking of the product in its category by revenue
    rank() over (
        partition by o.category
        order by cr.product_revenue_in_category desc
    )    as rank_in_category,

    -- metadata
    o.ingested_at

from orders o
inner join category_revenue cr
    on o.product_id = cr.product_id
    and o.category = cr.category