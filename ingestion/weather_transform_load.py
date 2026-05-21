import uuid
import pandas as pd
from sqlalchemy import text


weather_code_map = {
    0: "Clear",
    1: "Partly cloudy",
    2: "Partly cloudy",
    3: "Partly cloudy",
    45: "Foggy",
    48: "Foggy",
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    56: "Freezing Drizzle",
    57: "Freezing Drizzle",
    61: "Rain",
    63: "Rain",
    65: "Rain",
    66: "Freezing Rain",
    67: "Freezing Rain",
    71: "Snow",
    73: "Snow",
    75: "Snow",
    77: "Snow Grains",
    80: "Rain Showers",
    81: "Rain Showers",
    82: "Rain Showers",
    85: "Snow Showers",
    86: "Snow Showers",
}

def transform_hourly_weather(weather_data, location_id):
    hourly = weather_data["hourly"]

    df = pd.DataFrame(hourly)

    df["id"] = [uuid.uuid4() for _ in range(len(df))]
    df["location_id"] = location_id
    df['weather_description'] = df['weather_code'].map(weather_code_map)

    df.rename(
        columns={
            "time": "observed_at",
            "temperature_2m": "temperature",
            "apparent_temperature": "feels_like",
            "relative_humidity_2m": "humidity",
            "surface_pressure": "pressure",
            "wind_speed_10m": "wind_speed",
        },
        inplace=True,
    )

    wanted_columns = [
        "id",
        "location_id",
        "observed_at",
        "temperature",
        "feels_like",
        "humidity",
        "pressure",
        "wind_speed",
        "weather_code",
        "weather_description",
    ]

    existing_columns = [col for col in wanted_columns if col in df.columns]

    return df[existing_columns]

def load_weather_observations(df, engine):
    if df.empty:
        print("No weather observations to load.")
        return

    sql = text("""
        INSERT INTO weather_observation (
            id,
            location_id,
            observed_at,
            temperature,
            feels_like,
            humidity,
            pressure,
            wind_speed,
            weather_code,
            weather_description
        )
        VALUES (
            :id,
            :location_id,
            :observed_at,
            :temperature,
            :feels_like,
            :humidity,
            :pressure,
            :wind_speed,
            :weather_code,
            :weather_description
        )
        ON CONFLICT (location_id, observed_at)
        DO UPDATE SET
            temperature = EXCLUDED.temperature,
            feels_like = EXCLUDED.feels_like,
            humidity = EXCLUDED.humidity,
            pressure = EXCLUDED.pressure,
            wind_speed = EXCLUDED.wind_speed,
            weather_code = EXCLUDED.weather_code,
            weather_description = EXCLUDED.weather_description;
    """)

    records = df.to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(sql, records)

    print(f"Loaded or updated {len(records)} weather observation rows.")