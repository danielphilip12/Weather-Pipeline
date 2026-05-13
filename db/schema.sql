CREATE TABLE "location" (
  "id" uuid PRIMARY KEY,
  "city" text NOT NULL,
  "state" text,
  "country" text NOT NULL,
  "latitude" numeric NOT NULL,
  "longitude" numeric NOT NULL,
  "created_at" timestamptz DEFAULT (now())
);

CREATE TABLE "weather_observation" (
  "id" uuid PRIMARY KEY,
  "location_id" uuid NOT NULL,
  "observed_at" timestamptz NOT NULL,
  "temperature" numeric,
  "feels_like" numeric,
  "humidity" numeric,
  "pressure" numeric,
  "wind_speed" numeric,
  "weather_description" text,
  "weather_code" integer,
  "raw_json" jsonb,
  "created_at" timestamptz DEFAULT (now())
);

CREATE TABLE "daily_forecasts" (
  "id" uuid PRIMARY KEY,
  "location_id" uuid NOT NULL,
  "forecast_date" date NOT NULL,
  "temp_min" numeric,
  "temp_max" numeric,
  "precipitation_probability" numeric,
  "weather_description" text,
  "weather_code" integer,
  "raw_json" jsonb,
  "created_at" timestamptz DEFAULT (now())
);

CREATE UNIQUE INDEX ON "location" ("latitude", "longitude");

CREATE UNIQUE INDEX ON "weather_observation" ("location_id", "observed_at");

CREATE UNIQUE INDEX ON "daily_forecasts" ("location_id", "forecast_date");

ALTER TABLE "weather_observation" ADD FOREIGN KEY ("location_id") REFERENCES "location" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "daily_forecasts" ADD FOREIGN KEY ("location_id") REFERENCES "location" ("id") DEFERRABLE INITIALLY IMMEDIATE;
