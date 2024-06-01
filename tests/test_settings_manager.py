import unittest
from src.settings_manager import (
    load_settings,
    save_settings,
    validate_settings,
    save_locations,
    extract_units
)

class TestSettingsManager(unittest.TestCase):

    def test_load_settings(self):
        settings = load_settings()
        self.assertIsInstance(settings, dict)
        self.assertIn("temperature_unit", settings)

    def test_save_settings(self):
        new_settings = load_settings()
        new_settings["temperature_unit"] = "Fahrenheit °F"
        save_settings(new_settings)
        updated_settings = load_settings()
        self.assertEqual(updated_settings["temperature_unit"], "Fahrenheit °F")

    def test_validate_settings(self):
        self.assertRaises(ValueError, validate_settings, {"invalid_key": "invalid_value"})

    def test_save_locations(self):
        locations = [{"name": "San Francisco", "country": "USA", "latitude": 37.7749, "longitude": -122.4194}]
        save_locations(locations)
        updated_settings = load_settings()
        self.assertEqual(updated_settings["locations"], locations)

    def test_extract_units(self):
        temperature_unit, wind_speed_unit, precipitation_unit = extract_units()
        self.assertIsInstance(temperature_unit, str)
        self.assertIsInstance(wind_speed_unit, str)
        self.assertIsInstance(precipitation_unit, str)

if __name__ == "__main__":
    unittest.main()