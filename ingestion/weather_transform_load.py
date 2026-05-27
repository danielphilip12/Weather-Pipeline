import uuid
import pandas as pd
from pathlib import Path
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
    df["weather_description"] = df["weather_code"].map(weather_code_map)

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


def export_weather_observations_to_csv(df, csv_path):
    if df.empty:
        print("No weather observations to export.")
        return

    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(csv_path, index=False)

    print(f"Exported {len(df)} weather observation rows to {csv_path}.")


def load_weather_observations_from_csv(csv_path, engine):
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    copy_sql = """
        COPY weather_observation (
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
        FROM STDIN
        WITH (
            FORMAT csv,
            HEADER true
        );
    """

    with engine.begin() as conn:
        raw_conn = conn.connection
        cursor = raw_conn.cursor()

        with open(csv_path, "r", encoding="utf-8") as file:
            cursor.copy_expert(copy_sql, file)

    print(f"Loaded weather observations from {csv_path}.")

def clear_weather_observations(engine):
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE weather_observation;"))

    print("Cleared weather_observation table.")

def make_city_csv_filename(city, state):
    city_part = city.lower().replace(" ", "_")
    state_part = state.lower()

    return f"{city_part}_{state_part}.csv"

def load_weather_observations_from_csv_folder(folder_path, engine):
    folder_path = Path(folder_path)

    csv_files = sorted(folder_path.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {folder_path}.")
        return

    print(f"Found {len(csv_files)} CSV files to load.")

    for csv_file in csv_files:
        print(f"Loading {csv_file.name}...")
        load_weather_observations_from_csv(csv_file, engine)

    print("Finished loading all weather observation CSV files.")