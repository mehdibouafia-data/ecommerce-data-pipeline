-- Verify that the quantity ordered is strictly positive
select cart_id, product_id
from {{ ref('stg_cart_items') }}
where quantity <= 0
