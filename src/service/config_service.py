import json
from pathlib import Path

#import command for cogs:
#from src.service.config_service import Config

#path for config.json
config_file = Path(__file__).parents[2] / "resources" / "config" / "config.json"

class Config:
    def save(guild_id:str, setting:str, value:(str | int | float | bool)) -> None:
        """
        Saves a value to a setting bound to a server.
        :param guild_id: Identifier for the server
        :param setting: Setting name
        :param value: Value to set setting to
        """
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        with open(config_file, 'w') as f:
            config_data[guild_id] = ({setting: value})
            json_data = json.dumps(config_data)
            f.write(json_data)

    def load(guild_id:str, setting:str) -> (str | int | float | bool):
        """
        Loads a value from a setting bound to a server.
        :param guild_id: Identifier for the server
        :param setting: Setting name
        """
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            return config_data[guild_id][setting]
