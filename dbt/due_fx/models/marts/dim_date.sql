with 
    dates_raw as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2025-01-01' as date)",
        end_date="cast('2030-01-31' as date)"
        )
    }}
)

select 
    CAST(date_day AS DATE) as date_day,
    EXTRACT(dayofweek from date_day) as day_of_week,
    EXTRACT(month from date_day) as month_of_year,
    EXTRACT(year from date_day) as year,
    EXTRACT(quarter from date_day) as quarter,
    FORMAT_DATE('%B', date_day) as month_name,
    FORMAT_DATE('%A', date_day) as day_name,
    EXTRACT(dayofweek from date_day) IN (1,7) AS is_weekend,
    -- CASE 
    --     WHEN EXTRACT(dayofweek from date_day) IN (1,7) THEN True
    --     ELSE False
    -- END AS is_weekend
    CAST(FORMAT_DATE('%Y%m%d', date_day) AS INT64) as date_int,
    FORMAT_DATE('%Y-%m', date_day) as year_month
FROM dates_raw