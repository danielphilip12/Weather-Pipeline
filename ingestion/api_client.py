import requests
import os

BASE_URL = os.getenv("WEATHER_API_BASE_URL")

def fetch_weather(latitude, longitude):
    url = f"{BASE_URL}/forecast"

    params = {
        "latitude":latitude,
        "longitude": longitude,
        "hourly": "temperature_2m"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()