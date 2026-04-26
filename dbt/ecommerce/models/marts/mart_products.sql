with orders as (
    select * from {{ ref('int_orders_enriched') }}
),

aggregated as (
    select
        product_id,
        product_name,
        category,
        brand,
        rating,
        stock,

        count(distinct cart_id)                    as total_orders,
        sum(quantity)                              as total_units_sold,
        round(sum(item_total), 2)                  as total_revenue,
        round(sum(item_discounted_total), 2)       as total_revenue_discounted,
        round(avg(discount_percentage), 2)         as avg_discount_percentage,
        round(avg(unit_price), 2)                  as avg_unit_price,

        max(ingested_at)                           as last_ingested_at

    from orders
    group by
        product_id, product_name, category,
        brand, rating, stock
)


select
        *,

    -- Performance score: combines normalized rating + sales volume
    -- Rating out of 5 → weight 40% | Units sold normalized → weight 60%
    round(
        (rating / 5.0 * 0.4)
        + ( CAST(ln(1 + total_units_sold) AS NUMERIC) / nullif(max(ln(1 + total_units_sold)) over (), 0) * 0.6)
    , 4)   as performance_score,

    -- Global ranking by revenue
    rank() over (
        order by total_revenue_discounted desc
    )      as revenue_rank,

    -- Ranking by category by revenue
    rank() over (
        partition by category
        order by total_revenue_discounted desc
    )      as revenue_rank_in_category,

    -- Low stock alert (stock < 10% of the category's maximum)
    case
        when stock < 0.1 * max(stock) over (partition by category)
        then true
        else false
    end    as low_stock_alert

from aggregated
