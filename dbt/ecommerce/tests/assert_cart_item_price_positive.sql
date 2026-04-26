-- Verify that the unit price of the items is strictly positive
select cart_id, product_id
from {{ ref('stg_cart_items') }}
where price <= 0
