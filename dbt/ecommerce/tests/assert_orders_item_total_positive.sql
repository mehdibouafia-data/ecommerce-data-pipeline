-- Verify that the total of each order item is positive
select cart_id, product_id
from {{ ref('int_orders_enriched') }}
where item_total <= 0
