-- Verifies that the discounted total of an item is always less than or equal to the gross total
select cart_id, product_id
from {{ ref('mart_sales') }}
where item_discounted_total > item_total
