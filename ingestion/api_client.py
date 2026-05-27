import requests
import os
import time

BASE_URL = os.getenv("WEATHER_API_BASE_URL")

YEARS = [2023, 2024, 2025]


def fetch_weather(latitude, longitude, start_date, end_date, max_retries=3):
    url = f"{BASE_URL}/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "apparent_temperature",
            "relative_humidity_2m",
            "wind_speed_10m",
            "weather_code",
            "surface_pressure",
        ],
        "start_date": start_date,
        "end_date": end_date,
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=(10, 120))
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print(
                f"Timeout for lat={latitude}, lon={longitude}, "
                f"{start_date} to {end_date}. "
                f"Attempt {attempt}/{max_retries}."
            )

            if attempt == max_retries:
                raise

            time.sleep(5 * attempt)