from api_client import fetch_weather
from locations import get_locations

import os
import time
import uuid
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


load_dotenv()


DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "weather_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


def wait_for_database(max_attempts=10, delay_seconds=3):
    for attempt in range(max_attempts):
        try:
            with engine.connect():
                print("Connected to database.")
            return
        except OperationalError:
            print(f"Database not ready yet, retrying... ({attempt + 1}/{max_attempts})")
            time.sleep(delay_seconds)

    raise RuntimeError("Could not connect to the database.")


def load_locations(locations):
    sql = text("""
        INSERT INTO location (
            id,
            city,
            state,
            country,
            latitude,
            longitude
        )
        VALUES (
            :id,
            :city,
            :state,
            :country,
            :latitude,
            :longitude
        )
        ON CONFLICT (latitude, longitude)
        DO UPDATE SET
            city = EXCLUDED.city,
            state = EXCLUDED.state,
            country = EXCLUDED.country
        RETURNING id;
    """)

    location_ids = []

    with engine.begin() as conn:
        for location in locations:
            result = conn.execute(
                sql,
                {
                    "id": uuid.uuid4(),
                    "city": location["city"],
                    "state": location["state"],
                    "country": location["country"],
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                },
            )

            location_id = result.scalar_one()
            location_ids.append(location_id)

    print(f"Loaded or updated {len(location_ids)} locations.")
    return location_ids


def get_locations_from_db():
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM location", conn)


def transform_hourly_weather(weather_data, location_id):
    hourly = weather_data["hourly"]

    df = pd.DataFrame(hourly)

    df["id"] = [uuid.uuid4() for _ in range(len(df))]
    df["location_id"] = location_id

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
    ]

    existing_columns = [col for col in wanted_columns if col in df.columns]

    return df[existing_columns]


def load_weather_observations(df):
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
            weather_code
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
            :weather_code
        )
        ON CONFLICT (location_id, observed_at)
        DO UPDATE SET
            temperature = EXCLUDED.temperature,
            feels_like = EXCLUDED.feels_like,
            humidity = EXCLUDED.humidity,
            pressure = EXCLUDED.pressure,
            wind_speed = EXCLUDED.wind_speed,
            weather_code = EXCLUDED.weather_code;
    """)

    records = df.to_dict(orient="records")

    with engine.begin() as conn:
        conn.execute(sql, records)

    print(f"Loaded or updated {len(records)} weather observation rows.")


def main():
    print("Starting weather ingestion pipeline.")

    wait_for_database()

    locations = get_locations()

    # For early testing only.
    # Long-term, replace this with an upsert.
    load_locations(locations)

    locs = get_locations_from_db()

    for _, row in locs.iterrows():
        print(f"Fetching weather for {row['city']}...")

        weather_data = fetch_weather(row["latitude"], row["longitude"])

        weather_df = transform_hourly_weather(
            weather_data=weather_data,
            location_id=row["id"],
        )

        load_weather_observations(weather_df)

    print("Weather ingestion pipeline finished.")


if __name__ == "__main__":
    main()