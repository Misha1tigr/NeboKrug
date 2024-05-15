import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry


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
    if temperature_unit == "Fahrenheit °F":
        temperature_unit_ = "fahrenheit"
    else:
        temperature_unit_ = "celsius"
    if precipitation_unit == "Inch":
        precipitation_unit_ = "inch"
    else:
        precipitation_unit_ = "mm"
    if wind_speed_unit == "Km/h":
        wind_speed_unit_ = "kmh"
    elif wind_speed_unit == "m/s":
        wind_speed_unit_ = "ms"
    elif wind_speed_unit == "Knots":
        wind_speed_unit_ = "kn"
    else:
        wind_speed_unit_ = "mph"

    # Set up the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # URL and parameters for the API request
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

    # Making the API request
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Extract daily data
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

    # Creating DataFrame from the daily data
    daily_dataframe = pd.DataFrame(data=daily_data)

    return daily_dataframe


def search_location(query):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data.get('results', [])
