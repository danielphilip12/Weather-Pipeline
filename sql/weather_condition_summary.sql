select 
	city,
	weather_description,
	count(*)
from weather_observation wo
join location l
on wo.location_id = l.id
group by 1, 2
order by city, count(*) desc;
-- to run: Get-Content .\sql\weather_condition_summary.sql | docker compose exec -T db psql -U postgres -d weather_db