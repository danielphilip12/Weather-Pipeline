import requests
import os

BASE_URL = os.getenv("WEATHER_API_BASE_URL")

def fetch_weather(latitude, longitude):
    url = f"{BASE_URL}/forecast"

    params = {
        "latitude":latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "wind_speed_10m", "weather_code", 'surface_pressure'],
        "start_date": "2026-01-01",
        "end_date": "2026-04-30",

    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()