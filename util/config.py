import json
from typing import Iterable, Union


def load_config_file(file: str) -> json:
    """Attempts to load a json config file"""
    with open(file) as config:
        try:
            return json.load(config)
        except json.decoder.JSONDecodeError as err:
            raise Exception(
                f"Couldn't load {config}: it is formatted incorrectly "
                f"on line {err.lineno} column {err.colno}"
            ) from err



def get_config(item: str) -> Union[str, int]:
    """Retrieves the configuration value specified."""
    file = load_config_file("config.json")

    value = file.get(item)

    if value is None:
        raise Exception(f"Your config is out of date! Missing a value for {item}")
    return value