-- ─────────────────────────────────────────────────────────────
-- Top 5 products by category
-- Based on discounted revenue and performance score
-- Use case: merchandising, highlighting bestsellers
-- ─────────────────────────────────────────────────────────────

select
    category,
    product_id,
    product_name,
    brand,
    rating,
    total_units_sold,
    total_revenue_discounted,
    avg_discount_percentage,
    performance_score,
    revenue_rank_in_category

from {{ ref('mart_products') }}

where revenue_rank_in_category <= 5

order by
    category,
    revenue_rank_in_category