-- Verify that the stock is never negative
select product_id
from {{ ref('stg_products') }}
where stock < 0
