-- Verify that there are no items without a parent cart
select ci.cart_id
from {{ ref('stg_cart_items') }} ci
left join {{ ref('stg_carts') }} c on ci.cart_id = c.cart_id
where c.cart_id is null
