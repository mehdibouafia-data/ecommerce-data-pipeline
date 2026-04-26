-- ─────────────────────────────────────────────────────────────
-- Low stock products
-- Joins remaining stock with sales performance
-- Use case: priority restocking, supply chain management
-- ─────────────────────────────────────────────────────────────

select
    product_id,
    product_name,
    category,
    brand,
    stock                                               as remaining_stock,
    total_units_sold,
    total_revenue_discounted,
    performance_score,
    revenue_rank_in_category,

    -- Urgent restocking: high-performing products with critical stock levels at the forefront
    case
        when performance_score >= 0.7 then 'critical'
        when performance_score >= 0.4 then 'high'
        else 'medium'
    end                                                 as restock_priority

from {{ ref('mart_products') }}

where low_stock_alert = true

order by
    performance_score desc,
    remaining_stock asc