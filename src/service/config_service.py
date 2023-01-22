import json
from pathlib import Path
from typing import TypeVar

CONFIG_FILE = Path(__file__) / '../..resources/config/config.json'
JsonObject = TypeVar('JsonObject', str, int, float, bool, list, dict, None)


class Config:
    @staticmethod
    def create_config_if_not_exists():
        if not CONFIG_FILE.is_file():
            with open(CONFIG_FILE, 'w') as f:
                f.write('{}')

    @staticmethod
    def save(
            guild_id: str,
            setting: str,
            value: JsonObject
    ) -> None:
        """
        Saves a value to a setting bound to a server.
        :param guild_id: Identifier for the server
        :param setting: Setting name
        :param value: Value to set setting to
        """
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)

        if guild_id not in config_data:
            config_data[guild_id] = {}
        config_data[guild_id][setting] = value
        json_data = json.dumps(config_data)

        with open(CONFIG_FILE, 'w') as f:
            f.write(json_data)

    @staticmethod
    def load(
            guild_id: str,
            setting: str
    ) -> JsonObject:
        """
        Loads a value from a setting bound to a server.
        :param guild_id: Identifier for the server
        :param setting: Setting name
        """
        try:
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
                return config_data[guild_id][setting]
        except IOError:
            return None


Config.create_config_if_not_exists()
