with customers_orders as (
    select * from {{ ref('int_customers_orders') }}
),

aggregated as (
    select
        user_id,
        first_name,
        last_name,
        email,
        age,
        city,
        country,
        company_name,

        count(cart_id)                                          as total_orders,
        round(sum(cart_total), 2)                               as total_spent,
        round(sum(cart_discounted_total), 2)                    as total_spent_discounted,
        round(avg(cart_total), 2)                               as avg_order_value,
        round(sum(cart_total - cart_discounted_total), 2)       as total_savings,

        max(ingested_at)                                        as last_ingested_at

    from customers_orders
    group by
        user_id, first_name, last_name, email,
        age, city, country, company_name
)

select
    *,

    -- Segmentation by customer value (value based on total spending)
    case ntile(3) over (order by total_spent_discounted desc)
          when 1 then 'high_value'
        when 2 then 'mid_value'
        when 3 then 'low_value'
    end     as customer_segment,

    -- Global ranking of customers by spending
    rank() over (
        order by total_spent_discounted desc
    )       as customer_rank,

    -- Ranking by country
    rank() over (
        partition by country
        order by total_spent_discounted desc
    )       as customer_rank_in_country

from aggregated
