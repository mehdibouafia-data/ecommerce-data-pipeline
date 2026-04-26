with source as (
    select * from {{ source('raw', 'users') }}
    where id is not null
      and email is not null
)


select
    id                      as user_id,
    first_name,
    last_name,
    lower(trim(email))     as email,
    phone,
    age::integer           as age,
    city,
    country,
    company_name,
    ingested_at
from source