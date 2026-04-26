-- ─────────────────────────────────────────────────────────────
-- Product recommendations — simplified collaborative filtering
-- Logic: "customers who bought A also bought B"
-- Based on product co-occurrence in the same carts
--
-- Use case: recommendation engine, cross-selling, upselling
-- ─────────────────────────────────────────────────────────────

with product_pairs as (
    -- All pairs of products purchased in the same cart
    select
        a.product_id                                    as product_a_id,
        a.product_name                                  as product_a_name,
        a.category                                      as product_a_category,
        b.product_id                                    as product_b_id,
        b.product_name                                  as product_b_name,
        b.category                                      as product_b_category,
        count(distinct a.cart_id)                       as co_occurrence_count

    from {{ ref('mart_sales') }} a
    inner join {{ ref('mart_sales') }} b
        on  a.cart_id    = b.cart_id
        and a.product_id < b.product_id   -- avoids duplicates (A,B) and (B,A)

    group by
        a.product_id, a.product_name, a.category,
        b.product_id, b.product_name, b.category
),

ranked_recommendations as (
    select
        *,

        -- Ranking of top recommendations by source product
        rank() over (
            partition by product_a_id
            order by co_occurrence_count desc
        )                                               as recommendation_rank

    from product_pairs
)

select
    product_a_id,
    product_a_name,
    product_a_category,
    product_b_id                                        as recommended_product_id,
    product_b_name                                      as recommended_product_name,
    product_b_category                                  as recommended_product_category,
    co_occurrence_count,
    recommendation_rank

from ranked_recommendations

where recommendation_rank <= 3   -- top 3 recommendations per product

order by
    product_a_name,
    recommendation_rank