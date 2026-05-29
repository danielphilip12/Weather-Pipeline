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