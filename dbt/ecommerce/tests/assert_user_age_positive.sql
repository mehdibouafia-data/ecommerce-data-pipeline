-- Verify that the age of users is strictly positive
select user_id
from {{ ref('stg_users') }}
where age is not null and age <= 0
