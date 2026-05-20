select 
    city,
    round(avg(temperature), 2) as avg_temperature,
    round(avg(humidity), 2) as avg_humidity,
    round(avg(wind_speed), 2) as avg_wind_speed,
    max(temperature) as max_temperature,
    min(temperature) as min_temperature
from weather_observation wo
join location l
    on wo.location_id = l.id
group by city;

-- to run: Get-Content .\sql\city_comp.sql | docker compose exec -T db psql -U postgres -d weather_db