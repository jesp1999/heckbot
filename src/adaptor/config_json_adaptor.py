import json
import os
from pathlib import Path
from typing import TypeVar, Optional

from discord.ext.commands import Bot

JsonObject = TypeVar('JsonObject', str, int, float, bool, list, dict, None)


class ConfigJsonAdaptor:
    """
    Adaptor service for managing a configuration file on the local
    filesystem.
    """
    _config_file = (os.path.dirname(os.path.realpath(__file__)) +
                    '/../../resources/config/config.json')

    def __init(self):
        self.create_config_if_not_exists()

    def create_config_if_not_exists(
            self
    ):
        if not self._config_file.is_file():
            with open(self._config_file, 'w') as f:
                f.write('{}')

    def save(
            self,
            guild_id: str,
            *setting_parts
    ) -> None:
        """
        Saves a value to a setting bound to a server.
        :param guild_id: Identifier for the server
        :param setting: Setting name
        :param value: Value to set setting to
        """
        with open(self._config_file, 'r') as f:
            try:
                config_data = json.load(f)
            except Exception:
                config_data = {}

        if guild_id not in config_data:
            config_data[guild_id] = {}
        config_node = config_data[guild_id]
        for setting in setting_parts[:-2]:
            if setting not in config_node:
                config_node[setting] = {}
            config_node = config_node[setting]
        config_node[setting_parts[-2]] = setting_parts[-1]

        json_data = json.dumps(config_data, indent=4)

        with open(self._config_file, 'w') as f:
            f.write(json_data)

    def load(
            self,
            guild_id: str,
            *setting_parts
    ) -> JsonObject:
        """
        Loads a value from a setting bound to a server.
        :param guild_id: Identifier for the server
        :param setting: Setting name
        """
        with open(self._config_file, 'r') as f:
            config_data = json.load(f)
            config_node = config_data.get(guild_id, {})
            for setting in setting_parts:
                config_node = config_node.get(setting, {})
            return config_node or None

    def generate_default_config(
            self,
            bot: Bot,
            guild_id: str
    ):
        command_info = {(cmd.name, cmd.cog_name) for cmd in bot.commands}
        for command_name, module_name in command_info:
            self.save(
                guild_id,
                'modules',
                module_name,
                'commands',
                command_name,
                'enabled', 'true'
            )
