-- Verify that the discounted revenue is always less than or equal to the gross revenue
select product_id
from {{ ref('mart_products') }}
where total_revenue_discounted > total_revenue
