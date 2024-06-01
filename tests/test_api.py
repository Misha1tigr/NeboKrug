import unittest
from src.api import (
    get_historical_weather_data,
    get_forecast_data,
    get_current_weather,
    search_location,
    convert_units
)
import pandas as pd

class TestAPI(unittest.TestCase):

    def test_convert_units(self):
        temp_unit, wind_unit, precip_unit = convert_units("Fahrenheit °F", "Km/h", "Inch")
        self.assertEqual(temp_unit, "fahrenheit")
        self.assertEqual(wind_unit, "kmh")
        self.assertEqual(precip_unit, "inch")

    def test_get_historical_weather_data(self):
        latitude, longitude = 37.7749, -122.4194
        start_date, end_date = "2023-01-01", "2023-01-02"
        df = get_historical_weather_data(latitude, longitude, start_date, end_date)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("temperature_2m_max", df.columns)

    def test_get_forecast_data(self):
        latitude, longitude = 37.7749, -122.4194
        df = get_forecast_data(latitude, longitude)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn("temperature_2m", df.columns)

    def test_get_current_weather(self):
        latitude, longitude = 37.7749, -122.4194
        weather_data = get_current_weather(latitude, longitude)
        self.assertIn("Time:", weather_data)

    def test_search_location(self):
        results = search_location("San Francisco")
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        self.assertIn("name", results[0])

if __name__ == "__main__":
    unittest.main()