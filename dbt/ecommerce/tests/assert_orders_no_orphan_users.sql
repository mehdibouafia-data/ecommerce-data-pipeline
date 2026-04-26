-- Verify that there are no orders without a parent user
select c.cart_id
from {{ ref('stg_carts') }} c
left join {{ ref('stg_users') }} u on c.user_id = u.user_id
where u.user_id is null
