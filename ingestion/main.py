from api_client import fetch_weather
from locations import get_locations
from weather_transform_load import (
    transform_hourly_weather,
    load_weather_observations,
)

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

        load_weather_observations(weather_df, engine)

    print("Weather ingestion pipeline finished.")


if __name__ == "__main__":
    main()