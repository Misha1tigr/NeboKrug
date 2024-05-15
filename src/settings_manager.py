import json
import platformdirs
import os
from jsonschema import validate, ValidationError

settings_schema = {
    "type": "object",
    "properties": {
        "temperature_unit": {"type": "string", "enum": ["Celsius °C", "Fahrenheit °F"]},
        "wind_speed_unit": {"type": "string", "enum": ["Km/h", "m/s", "Mph", "Knots"]},
        "precipitation_unit": {"type": "string", "enum": ["Millimeter", "Inch"]},
    },
    "required": ["temperature_unit", "wind_speed_unit", "precipitation_unit"],
}


def get_settings_path():
    settings_dir = platformdirs.user_config_dir("NeboKrug", "Korbut Mykhailo")
    os.makedirs(settings_dir, exist_ok=True)
    return os.path.join(settings_dir, "settings.json")


def load_settings():
    settings_path = get_settings_path()
    if os.path.exists(settings_path):
        with open(settings_path, "r") as file:
            settings = json.load(file)
            validate_settings(settings)
            print(settings)  #TODO remove
            return settings
    return {}


def save_settings(settings):
    validate_settings(settings)
    settings_path = get_settings_path()
    with open(settings_path, "w") as file:
        json.dump(settings, file)


def validate_settings(settings):
    try:
        validate(instance=settings, schema=settings_schema)
    except ValidationError as e:
        raise ValueError(f"Invalid settings: {e.message}")
