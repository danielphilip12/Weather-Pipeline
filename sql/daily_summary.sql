select
    city,
    to_char(observed_at, 'YYYY-MM-DD') as observation_date,
    round(avg(temperature), 2) as avg_temperature,
    min(temperature) as min_temperature,
    max(temperature) as max_temperature,
    round(avg(humidity), 2) as avg_humidity,
    round(avg(wind_speed), 2) as avg_wind_speed,
    count(*) as observation_count
from weather_observation wo
join location l
    on wo.location_id = l.id
group by observation_date, city
order by city, observation_date;










-- to run: Get-Content .\sql\daily_summary.sql | docker compose exec -T db psql -U postgres -d weather_db