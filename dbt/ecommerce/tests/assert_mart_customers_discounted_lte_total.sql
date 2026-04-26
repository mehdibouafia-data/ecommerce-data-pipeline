-- Verifies that a customer's discounted total is always less than or equal to their gross total
select user_id
from {{ ref('mart_customers') }}
where total_spent_discounted > total_spent
