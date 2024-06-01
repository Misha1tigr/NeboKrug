import unittest
from src.settings_manager import load_settings, extract_units

class TestMain(unittest.TestCase):

    def test_load_settings(self):
        settings = load_settings()
        self.assertIsInstance(settings, dict)
        self.assertIn("temperature_unit", settings)

    def test_extract_units(self):
        temperature_unit, wind_speed_unit, precipitation_unit = extract_units()
        self.assertIsInstance(temperature_unit, str)
        self.assertIsInstance(wind_speed_unit, str)
        self.assertIsInstance(precipitation_unit, str)

if __name__ == "__main__":
    unittest.main()