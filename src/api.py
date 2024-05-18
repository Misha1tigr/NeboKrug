import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime
from ai_prompts import UA_prompt


def setup_openmeteo_client(cache_expire_after=3600):
    """
    Sets up the Open-Meteo API client with caching and retry on errors.

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
    Converts unit strings to Open-Meteo compliant format.

    Args:
        temperature_unit (str, optional): Unit for temperature. Defaults to 'celsius'.
        wind_speed_unit (str, optional): Unit for wind speed. Defaults to 'm/s'.
        precipitation_unit (str, optional): Unit for precipitation. Defaults to 'mm'.

    Returns:
        tuple: Converted units for temperature, wind speed, and precipitation.
    """
    temperature_unit_map = {"Fahrenheit °F": "fahrenheit", "celsius": "celsius"}
    precipitation_unit_map = {"Inch": "inch", "mm": "mm"}
    wind_speed_unit_map = {"Km/h": "kmh", "m/s": "ms", "Knots": "kn", "mph": "mph"}

    return (
        temperature_unit_map.get(temperature_unit, "celsius"),
        wind_speed_unit_map.get(wind_speed_unit, "ms"),
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
        temperature_unit (str, optional): Unit for temperature. Defaults to 'celsius'.
        wind_speed_unit (str, optional): Unit for wind speed. Defaults to 'm/s'.
        precipitation_unit (str, optional): Unit for precipitation. Defaults to 'mm'.

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
        temperature_unit (str, optional): Unit for temperature. Defaults to 'celsius'.
        wind_speed_unit (str, optional): Unit for wind speed. Defaults to 'm/s'.
        precipitation_unit (str, optional): Unit for precipitation. Defaults to 'mm'.

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


def get_current_weather(latitude, longitude, temperature_unit="celsius",
                        wind_speed_unit="m/s", precipitation_unit="mm"):
    """
    Fetches current weather data for specified coordinates.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        temperature_unit (str, optional): Unit for temperature. Defaults to 'celsius'.
        wind_speed_unit (str, optional): Unit for wind speed. Defaults to 'm/s'.
        precipitation_unit (str, optional): Unit for precipitation. Defaults to 'mm'.

    Returns:
        str: Formatted string containing the current weather data.
    """
    temperature_unit_, wind_speed_unit_, precipitation_unit_ = convert_units(
        temperature_unit, wind_speed_unit, precipitation_unit
    )

    openmeteo = setup_openmeteo_client()

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["relative_humidity_2m", "apparent_temperature", "rain", "showers", "snowfall", "wind_speed_10m",
                    "wind_gusts_10m"],
        "hourly": "temperature_2m",
        "temperature_unit": temperature_unit_,
        "wind_speed_unit": wind_speed_unit_,
        "precipitation_unit": precipitation_unit_,
        "timezone": "auto"
    }

    # Fetch weather data
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    current = response.Current()

    current_relative_humidity_2m = current.Variables(0).Value()
    current_apparent_temperature = current.Variables(1).Value()
    current_rain = current.Variables(2).Value()
    current_showers = current.Variables(3).Value()
    current_snowfall = current.Variables(4).Value()
    current_wind_speed_10m = current.Variables(5).Value()
    current_wind_gusts_10m = current.Variables(6).Value()

    # Get the current system time in HH:mm format
    current_system_time = datetime.now().strftime("%H:%M")

    # Format the current weather data into a string
    weather_string = (
        f"Time: {current_system_time}, "
        f"Apparent Temperature: {round(current_apparent_temperature, 1)} {temperature_unit_}, "
        f"Relative Humidity: {round(current_relative_humidity_2m, 1)}%, "
        f"Rain: {round(current_rain, 1)} {precipitation_unit_}, "
        f"Showers: {round(current_showers, 1)} {precipitation_unit_}, "
        f"Snowfall: {round(current_snowfall, 1)} {precipitation_unit_}, "
        f"Wind Speed: {round(current_wind_speed_10m, 1)} {wind_speed_unit_}, "
        f"Wind Gusts: {round(current_wind_gusts_10m, 1)} {wind_speed_unit_}"
    )
    return weather_string


def get_history_of_date(latitude, longitude, temperature_unit="celsius", wind_speed_unit="m/s",
                        precipitation_unit="mm"):
    """
    Fetches historical weather data for a specified location on this date for years starting from 1945.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        temperature_unit (str, optional): Unit for temperature. Defaults to 'celsius'.
        wind_speed_unit (str, optional): Unit for wind speed. Defaults to 'm/s'.
        precipitation_unit (str, optional): Unit for precipitation. Defaults to 'mm'.

    Returns:
        tuple: DataFrames containing today's weather data and historical weather data.
    """
    temperature_unit_, wind_speed_unit_, precipitation_unit_ = convert_units(
        temperature_unit, wind_speed_unit, precipitation_unit
    )

    openmeteo = setup_openmeteo_client()

    # Fetch current weather data
    current_url = "https://api.open-meteo.com/v1/forecast"
    current_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"],
        "temperature_unit": temperature_unit_,
        "wind_speed_unit": wind_speed_unit_,
        "precipitation_unit": precipitation_unit_,
        "timezone": "auto"
    }

    current_responses = openmeteo.weather_api(current_url, params=current_params)
    current_response = current_responses[0]
    current_daily = current_response.Daily()

    today_data = {
        "date": [pd.to_datetime(current_daily.Time(), unit="s", utc=True)],
        "temperature_2m_max": [current_daily.Variables(0).ValuesAsNumpy()[0]],
        "temperature_2m_min": [current_daily.Variables(1).ValuesAsNumpy()[0]],
        "precipitation_sum": [current_daily.Variables(2).ValuesAsNumpy()[0]],
        "wind_speed_10m_max": [current_daily.Variables(3).ValuesAsNumpy()[0]]
    }
    today_dataframe = pd.DataFrame(data=today_data)

    # Fetch historical weather data
    historical_url = "https://archive-api.open-meteo.com/v1/archive"
    today = datetime.now()
    historical_data = []

    for year in range(1945, today.year):
        date_str = today.replace(year=year).strftime('%Y-%m-%d')
        historical_params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date_str,
            "end_date": date_str,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"],
            "temperature_unit": temperature_unit_,
            "wind_speed_unit": wind_speed_unit_,
            "precipitation_unit": precipitation_unit_,
            "timezone": "auto"
        }
        historical_responses = openmeteo.weather_api(historical_url, params=historical_params)
        historical_response = historical_responses[0]
        historical_daily = historical_response.Daily()

        historical_data.append({
            "date": pd.to_datetime(historical_daily.Time(), unit="s", utc=True),
            "temperature_2m_max": historical_daily.Variables(0).ValuesAsNumpy()[0],
            "temperature_2m_min": historical_daily.Variables(1).ValuesAsNumpy()[0],
            "precipitation_sum": historical_daily.Variables(2).ValuesAsNumpy()[0],
            "wind_speed_10m_max": historical_daily.Variables(3).ValuesAsNumpy()[0]
        })

    historical_dataframe = pd.DataFrame(data=historical_data)
    return today_dataframe, historical_dataframe


def compare_todays_data(today_df, historical_df):
    """
    Compares today's weather data with historical data and generates a comparison report.

    Args:
        today_df (pd.DataFrame): DataFrame containing today's weather data.
        historical_df (pd.DataFrame): DataFrame containing historical weather data.

    Returns:
        str: Comparison report.
    """
    report = []

    # Max and Min Temperature Analysis
    today_max_temp = today_df['temperature_2m_max'].values[0]
    today_min_temp = today_df['temperature_2m_min'].values[0]
    historical_sorted_by_max_temp = historical_df.sort_values(by='temperature_2m_max', ascending=False)
    historical_sorted_by_min_temp = historical_df.sort_values(by='temperature_2m_min', ascending=True)

    hottest_year = historical_sorted_by_max_temp.iloc[0]['date'].year
    hottest_temp = historical_sorted_by_max_temp.iloc[0]['temperature_2m_max']
    coldest_year = historical_sorted_by_min_temp.iloc[0]['date'].year
    coldest_temp = historical_sorted_by_min_temp.iloc[0]['temperature_2m_min']

    max_temp_rank = (historical_sorted_by_max_temp['temperature_2m_max'] >= today_max_temp).sum()
    min_temp_rank = (historical_sorted_by_min_temp['temperature_2m_min'] <= today_min_temp).sum()

    if max_temp_rank == 1:
        temp_rank_text = f"Today is the hottest day on this date since 1945"
    elif min_temp_rank == 1:
        temp_rank_text = f"Today is the coldest day on this date since 1945"
    else:
        if max_temp_rank >= min_temp_rank:
            temp_rank_text = f"Today is the {max_temp_rank}-th hottest day on this date since 1945"
        else:
            temp_rank_text = f"Today is the {min_temp_rank}-th coldest day on this date since 1945"

    report.append(
        f"{temp_rank_text}, with the hottest being in {hottest_year} with a max temperature of {hottest_temp:.1f}°C, "
        f"and the coldest being in {coldest_year} with a min temperature of {coldest_temp:.1f}°C."
    )

    # Precipitation Analysis
    today_precipitation = today_df['precipitation_sum'].values[0]
    if today_precipitation == 0:
        last_rain_year = historical_df[historical_df['precipitation_sum'] > 0].iloc[-1]['date'].year
        last_rain_amount = historical_df[historical_df['precipitation_sum'] > 0].iloc[-1]['precipitation_sum']
        report.append(f"Last rain on this date was in {last_rain_year} with {last_rain_amount:.1f} mm of rain.")
    else:
        max_precipitation = historical_df['precipitation_sum'].max()
        if today_precipitation > max_precipitation:
            report.append(
                f"Today has the highest precipitation on this date since 1945 with {today_precipitation:.1f} mm of "
                f"rain.")
        else:
            wettest_year = historical_df.loc[historical_df['precipitation_sum'].idxmax(), 'date'].year
            report.append(
                f"Today has {today_precipitation:.1f} mm of rain. The wettest day on this date since 1945 was in "
                f"{wettest_year} with {max_precipitation:.1f} mm of rain.")

    # Wind Speed Analysis
    today_wind_speed = today_df['wind_speed_10m_max'].values[0]
    historical_sorted_by_wind_speed = historical_df.sort_values(by='wind_speed_10m_max', ascending=False)
    historical_sorted_by_calm_wind = historical_df.sort_values(by='wind_speed_10m_max', ascending=True)

    max_wind_speed_year = historical_sorted_by_wind_speed.iloc[0]['date'].year
    max_wind_speed = historical_sorted_by_wind_speed.iloc[0]['wind_speed_10m_max']
    calmest_wind_year = historical_sorted_by_calm_wind.iloc[0]['date'].year
    calmest_wind_speed = historical_sorted_by_calm_wind.iloc[0]['wind_speed_10m_max']

    wind_speed_rank = (historical_sorted_by_wind_speed['wind_speed_10m_max'] >= today_wind_speed).sum()

    if wind_speed_rank == 1:
        wind_speed_text = f"Today has the highest wind speed on this date since 1945"
    else:
        wind_speed_text = f"Today is the {wind_speed_rank}-th windiest day on this date since 1945"

    report.append(
        f"{wind_speed_text}, with the highest wind speed being in {max_wind_speed_year} with {max_wind_speed:.1f}"
        f" m/s, and the calmest in {calmest_wind_year} with {calmest_wind_speed:.1f} m/s."
    )

    return "\n\n".join(report)


def get_clothing_recommendations(latitude, longitude, temperature_unit="celsius",
                                 wind_speed_unit="m/s", precipitation_unit="mm"):
    """
    Fetches clothing recommendations based on current weather data for the specified location.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        temperature_unit (str, optional): Unit for temperature. Defaults to 'celsius'.
        wind_speed_unit (str, optional): Unit for wind speed. Defaults to 'm/s'.
        precipitation_unit (str, optional): Unit for precipitation. Defaults to 'mm'.

    Returns:
        str: Clothing recommendations.
    """
    api_url = "http://misha1tigr.pythonanywhere.com/generate"
    current_weather = get_current_weather(latitude, longitude, temperature_unit,
                                          wind_speed_unit, precipitation_unit)
    prompt_text = UA_prompt + current_weather
    response = requests.post(api_url, json={"prompt": prompt_text})

    if response.status_code == 200:
        return response.json()["response"]
    else:
        return "Помилка при завантаженні даних"


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
