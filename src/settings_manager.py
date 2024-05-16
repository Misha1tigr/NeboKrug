import json
import platformdirs
import os
from jsonschema import validate, ValidationError

settings_schema = {
    "type": "object",
    "properties": {
        "temperature_unit": {"type": "string", "enum": ["Celsius °C", "Fahrenheit °F"]},
        "wind_speed_unit": {"type": "string", "enum": ["Km/h", "m/s", "mph", "Knots"]},
        "precipitation_unit": {"type": "string", "enum": ["Millimeter", "Inch"]},
        "locations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "country": {"type": "string"},
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["name", "country", "latitude", "longitude"]
            }
        }
    },
    "required": ["temperature_unit", "wind_speed_unit", "precipitation_unit"]
}

settings_loaded = False
settings = {}


def get_settings_path():
    settings_dir = platformdirs.user_config_dir("NeboKrug", "Korbut Mykhailo")
    os.makedirs(settings_dir, exist_ok=True)
    return os.path.join(settings_dir, "settings.json")


def load_settings():
    global settings_loaded, settings
    if not settings_loaded:
        settings_path = get_settings_path()
        if os.path.exists(settings_path):
            with open(settings_path, "r") as file:
                settings = json.load(file)
                validate_settings(settings)
                settings_loaded = True
                return settings
    else:
        return settings


def save_settings(new_settings):
    global settings
    try:
        validate_settings(new_settings)
        settings_path = get_settings_path()
        with open(settings_path, "w") as file:
            json.dump(new_settings, file)
    except Exception as e:
        print(f"Error saving settings: {e}")
    settings = new_settings


def validate_settings(settings_for_validation):
    try:
        validate(instance=settings_for_validation, schema=settings_schema)
    except ValidationError as e:
        raise ValueError(f"Invalid settings: {e.message}")



def save_locations(locations):
    settings_to_update = load_settings()
    settings_to_update["locations"] = locations
    save_settings(settings_to_update)


def extract_units():
    settings_to_extract_from = load_settings()
    temperature_unit = settings_to_extract_from.get("temperature_unit")
    wind_speed_unit = settings_to_extract_from.get("wind_speed_unit")
    precipitation_unit = settings_to_extract_from.get("precipitation_unit")
    return temperature_unit, wind_speed_unit, precipitation_unit
