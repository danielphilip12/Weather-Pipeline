create view avg_daily_stats as 
select 
    city,
    state,
    observed_at::date as observed_date,
    round(avg(temperature)::numeric, 2) as avg_temperature,
    round(avg(feels_like)::numeric, 2) as avg_feels_like,
    round(avg(humidity)::numeric, 2) as avg_humidity,
    round(avg(pressure)::numeric, 2) as avg_pressure,
    round(avg(wind_speed)::numeric, 2) as avg_wind_speed
from weather_observation wo
join location l
    on wo.location_id = l.id
group by city, state, observed_at::date;

create view full_table as
select
    wo.id as weather_observation_id,
    wo.location_id,
    wo.observed_at,
    wo.temperature,
    wo.feels_like,
    wo.humidity,
    wo.pressure,
    wo.wind_speed,
    wo.weather_description,
    wo.weather_code,
    wo.raw_json,
    wo.created_at as weather_observation_created_at,
    l.city,
    l.state,
    l.country,
    l.latitude,
    l.longitude,
    l.created_at as location_created_at
from weather_observation wo
join location l
    on wo.location_id = l.id;