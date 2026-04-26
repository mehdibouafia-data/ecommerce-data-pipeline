-- Verify that the customer ranking is always >= 1
select user_id
from {{ ref('mart_customers') }}
where customer_rank < 1
