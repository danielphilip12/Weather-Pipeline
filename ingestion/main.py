from api_client import fetch_weather
from locations import get_locations
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os
import uuid

load_dotenv()

LOCATIONS = get_locations()



DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "weather_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(DATABASE_URL)


engine = create_engine(DATABASE_URL)

for attempt in range(10):
    try:
        with engine.connect() as conn:
            print("Connected to database.")
        break
    except OperationalError:
        print(f"Database not ready yet, retrying... ({attempt + 1}/10)")
        time.sleep(3)
else:
    raise RuntimeError("Could not connect to the database.")


def load_locations(locations):
    df = pd.DataFrame(locations)
    df["id"] = [uuid.uuid4() for _ in range(len(df))]

    with engine.begin() as conn:
        df.to_sql("location", conn, if_exists="append", index=False)

    return "Table Loaded"



print(load_locations(LOCATIONS))


# for location in LOCATIONS:
#     print(fetch_weather(location['latitude'], location['longitude']))