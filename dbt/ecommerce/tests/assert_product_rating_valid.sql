-- Verify that the rating is between 0 and 5
select product_id
from {{ ref('stg_products') }}
where rating < 0 or rating > 5
