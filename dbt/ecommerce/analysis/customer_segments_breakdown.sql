-- ──────────────────────────────────────────────────────────────────────
-- Breakdown of customer segments
-- Distribution, revenue, and behavior by segment
-- Use case: targeted marketing, acquisition/retention budgets
-- ─────────────────────────────────────────────────────────────

select
    customer_segment,

    -- Volume
    count(user_id)                                      as nb_customers,
    round(
        count(user_id) * 100.0 / sum(count(user_id)) over ()
    , 2)                                                as pct_customers,

    -- Revenue
    round(sum(total_spent_discounted), 2)               as segment_revenue,
    round(
        sum(total_spent_discounted) * 100.0
        / nullif(sum(sum(total_spent_discounted)) over (), 0)
    , 2)                                                as pct_revenue,

    -- Behavior
    round(avg(total_orders), 2)                         as avg_orders_per_customer,
    round(avg(avg_order_value), 2)                      as avg_order_value,
    round(avg(total_savings), 2)                        as avg_savings_per_customer

from {{ ref('mart_customers') }}

group by customer_segment

order by
    case customer_segment
        when 'high_value'  then 1
        when 'mid_value'   then 2
        when 'low_value'   then 3
    end