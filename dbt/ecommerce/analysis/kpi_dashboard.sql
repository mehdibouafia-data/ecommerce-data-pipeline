-- ─────────────────────────────────────────────────────────────
-- KPI Dashboard — synthetic view of key metrics
-- Use case: executive reporting, weekly/monthly tracking
-- ─────────────────────────────────────────────────────────────

with sales_kpis as (
    select
        count(distinct cart_id)                         as total_orders,
        count(distinct user_id)                         as total_active_customers,
        count(distinct product_id)                      as total_products_sold,
        sum(quantity)                                   as total_units_sold,
        round(sum(item_total), 2)                       as gross_revenue,
        round(sum(item_discounted_total), 2)            as net_revenue,
        round(sum(item_total - item_discounted_total), 2) as total_discount_amount,
        round(avg(item_discounted_total), 2)            as avg_item_value
    from {{ ref('mart_sales') }}
),

cart_kpis as (
    select
        round(avg(total_spent_discounted), 2)           as avg_customer_ltv,
        round(avg(avg_order_value), 2)                  as avg_cart_value,
        round(avg(total_orders), 2)                     as avg_orders_per_customer,
        round(avg(total_savings), 2)                    as avg_savings_per_customer
    from {{ ref('mart_customers') }}
),

product_kpis as (
    select
        count(case when low_stock_alert then 1 end)     as products_low_stock,
        round(avg(performance_score), 4)                as avg_performance_score,
        round(avg(rating), 2)                           as avg_product_rating
    from {{ ref('mart_products') }}
)

select
    -- Revenue
    s.gross_revenue,
    s.net_revenue,
    s.total_discount_amount,
    round(s.total_discount_amount * 100.0 / nullif(s.gross_revenue, 0), 2) as discount_rate_pct,

    -- Orders
    s.total_orders,
    s.total_units_sold,
    s.avg_item_value,
    c.avg_cart_value,

    -- Customers
    s.total_active_customers,
    c.avg_customer_ltv,
    c.avg_orders_per_customer,
    c.avg_savings_per_customer,

    -- Products
    s.total_products_sold,
    p.products_low_stock,
    p.avg_performance_score,
    p.avg_product_rating

from sales_kpis s
cross join cart_kpis c
cross join product_kpis p