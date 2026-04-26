-- Check that the item discount is between 0 and 100
select cart_id, product_id
from {{ ref('stg_cart_items') }}
where discount_percentage < 0 or discount_percentage > 100
