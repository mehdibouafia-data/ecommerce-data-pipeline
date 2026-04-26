-- Verify that the ranking revenue is always >= 1
select product_id
from {{ ref('mart_products') }}
where revenue_rank < 1
 
