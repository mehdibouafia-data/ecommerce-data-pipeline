-- Verifies that each customer has a strictly positive total spend
select user_id
from {{ ref('mart_customers') }}
where total_spent <= 0
 
