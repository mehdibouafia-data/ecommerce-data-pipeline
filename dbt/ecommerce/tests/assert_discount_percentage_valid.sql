-- Check that the discount is between 0 and 100
select product_id
from {{ ref('stg_products') }}
where discount_percentage < 0 or discount_percentage > 100
