-- Check that the performance score is between 0 and 1
select product_id
from {{ ref('mart_products') }}
where performance_score < 0 or performance_score > 1
