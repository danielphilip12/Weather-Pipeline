# Weather Data Pipeline

A Python and PostgreSQL data pipeline that collects weather data, stores it in a database, and prepares it for analysis using SQL, Python, and dashboarding tools.

## Project Overview

This project is designed to practice building a small data pipeline from end to end. It collects weather data for selected locations, stores raw and structured weather observations in PostgreSQL, and supports analysis through SQL queries, notebooks, and future dashboard tools.

## Goals

- Collect weather data from an external API
- Store weather observations in a PostgreSQL database
- Use Docker to manage the database and development environment
- Create Jupyter Notebooks for preliminary analysis and visualization
- Write SQL queries for weather analysis
- Practice data cleaning, transformation, and reporting
- Prepare the data for future dashboarding in Power BI or Streamlit

## Tech Stack

- Python
- PostgreSQL
- Docker / Docker Compose
- pgAdmin
- Pandas
- SQLAlchemy
- Jupyter Notebook
- SQL


## API Reference

This project uses the Open-Meteo Historical Forecast API as the weather data source.

- Website: https://open-meteo.com/
- API Documentation: https://open-meteo.com/en/docs/historical-forecast-api

Open-Meteo is used to retrieve weather data such as temperature, humidity, wind speed, precipitation probability, and weather codes.