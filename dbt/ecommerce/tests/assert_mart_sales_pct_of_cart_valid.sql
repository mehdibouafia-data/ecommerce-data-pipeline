-- Check that the contribution of each item to the cart is between 0 and 1
select cart_id, product_id
from {{ ref('mart_sales') }}
where pct_of_cart < 0 or pct_of_cart > 1
