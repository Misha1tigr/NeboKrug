import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry


def setup_openmeteo_client(cache_expire_after=3600):
    """
    Sets up the Open-Meteo API client with cache and retry on error.

    Args:
        cache_expire_after (int, optional): Cache expiration time in seconds. Defaults to 3600 seconds.

    Returns:
        openmeteo_requests.Client: Open-Meteo API client instance.
    """
    cache_session = requests_cache.CachedSession('.cache', expire_after=cache_expire_after)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)


def convert_units(temperature_unit="celsius", wind_speed_unit="m/s", precipitation_unit="mm"):
    """
    Converts units to Open-Meteo compliant unit strings.

    Args:
        temperature_unit (str, optional): Units for temperature. Defaults to 'celsius'.
        wind_speed_unit (str, optional): Units for wind speed. Defaults to 'm/s'.
        precipitation_unit (str, optional): Units for precipitation. Defaults to 'mm'.

    Returns:
        tuple: Converted units for temperature, wind speed, and precipitation.
    """
    temperature_unit_map = {"Fahrenheit °F": "fahrenheit", "celsius": "celsius"}
    precipitation_unit_map = {"Inch": "inch", "mm": "mm"}
    wind_speed_unit_map = {"Km/h": "kmh", "m/s": "ms", "Knots": "kn", "mph": "mph"}

    return (
        temperature_unit_map.get(temperature_unit, "celsius"),
        wind_speed_unit_map.get(wind_speed_unit, "mph"),
        precipitation_unit_map.get(precipitation_unit, "mm")
    )


def get_historical_weather_data(latitude, longitude, start_date, end_date, temperature_unit="celsius",
                                wind_speed_unit="m/s", precipitation_unit="mm"):
    """
    Fetches historical weather data for specified coordinates and date range.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        start_date (str): Start date for the data in 'YYYY-MM-DD' format.
        end_date (str): End date for the data in 'YYYY-MM-DD' format.
        temperature_unit (str, optional): Units for temperature. Defaults to 'celsius'.
        wind_speed_unit (str, optional): Units for wind speed. Defaults to 'm/s'.
        precipitation_unit (str, optional): Units for precipitation. Defaults to 'mm'.

    Returns:
        pd.DataFrame: DataFrame containing the historical weather data.
    """
    temperature_unit_, wind_speed_unit_, precipitation_unit_ = convert_units(
        temperature_unit, wind_speed_unit, precipitation_unit
    )

    openmeteo = setup_openmeteo_client()

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "daylight_duration",
                  "precipitation_sum", "wind_speed_10m_max"],
        "temperature_unit": temperature_unit_,
        "wind_speed_unit": wind_speed_unit_,
        "precipitation_unit": precipitation_unit_,
        "timezone": "auto"
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    daily = response.Daily()
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "temperature_2m_max": daily.Variables(0).ValuesAsNumpy(),
        "temperature_2m_min": daily.Variables(1).ValuesAsNumpy(),
        "temperature_2m_mean": daily.Variables(2).ValuesAsNumpy(),
        "daylight_duration": daily.Variables(3).ValuesAsNumpy(),
        "precipitation_sum": daily.Variables(4).ValuesAsNumpy(),
        "wind_speed_10m_max": daily.Variables(5).ValuesAsNumpy()
    }

    daily_dataframe = pd.DataFrame(data=daily_data)
    return daily_dataframe


def get_forecast_data(latitude, longitude, temperature_unit="celsius", wind_speed_unit="m/s", precipitation_unit="mm"):
    """
    Fetches forecast weather data for specified coordinates.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        temperature_unit (str, optional): Units for temperature. Defaults to 'celsius'.
        wind_speed_unit (str, optional): Units for wind speed. Defaults to 'm/s'.
        precipitation_unit (str, optional): Units for precipitation. Defaults to 'mm'.

    Returns:
        pd.DataFrame: DataFrame containing the forecast weather data.
    """
    temperature_unit_, wind_speed_unit_, precipitation_unit_ = convert_units(
        temperature_unit, wind_speed_unit, precipitation_unit
    )

    openmeteo = setup_openmeteo_client()

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation_probability",
                   "precipitation", "surface_pressure", "visibility", "wind_speed_10m", "uv_index"],
        "forecast_days": 14,
        "temperature_unit": temperature_unit_,
        "wind_speed_unit": wind_speed_unit_,
        "precipitation_unit": precipitation_unit_,
        "timezone": "auto"
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
        "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
        "apparent_temperature": hourly.Variables(2).ValuesAsNumpy(),
        "precipitation_probability": hourly.Variables(3).ValuesAsNumpy(),
        "precipitation": hourly.Variables(4).ValuesAsNumpy(),
        "surface_pressure": hourly.Variables(5).ValuesAsNumpy(),
        "visibility": hourly.Variables(6).ValuesAsNumpy(),
        "wind_speed_10m": hourly.Variables(7).ValuesAsNumpy(),
        "uv_index": hourly.Variables(8).ValuesAsNumpy()
    }

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    return hourly_dataframe


def search_location(query):
    """
    Searches for a location by name using the Open-Meteo geocoding API.

    Args:
        query (str): The name of the location to search for.

    Returns:
        list: A list of matching locations.
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data.get('results', [])