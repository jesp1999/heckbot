from __future__ import annotations

import os

import yaml


class ConfigAdaptor:
    def __init__(
            self,
    ):
        # guild_id -> group_name -> option -> value OR nested option
        self.configs: dict[
            str, dict[
                str, dict[
                    str, (
                        str | int | bool | dict[str, str | int | bool]
                    ),
                ],
            ],
        ] = {}
        self.config_file: str = os.getcwd() + '/../../../resources/config/config.yaml'

    def get_config(
            self,
            guild_id: int,
            group: str,
    ) -> dict[str, str | int | float | bool]:
        if str(guild_id) not in self.configs:
            # Load the config for the guild if it doesn't exist in memory
            self.load_config(guild_id)

        return self.configs[str(guild_id)].get(group, {})

    def load_config(
            self,
            guild_id: int,
    ):
        # Load the config from the file
        data = {}
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

        guild_config = data.get(str(guild_id), {})
        self.configs[str(guild_id)] = guild_config

        # Generate default values if not present

        default_message_info = {
            'welcomeMessage': 'Welcome to HeckBoiCrue <@!{}>!',
            'botOnlineMessage': 'hello, i am online',
            'guildJoinMessageTitle': '',
            'guildJoinMessage': '',
            'higherPermissionErrorMessage':
                'Error: The specified user has higher permissions than you.',
            'equalPermissionErrorMessage':
                'Error: The specified user has higher permissions than you or '
                'equal permissions.',
        }

        default_color_info = {
            'embedColor': '0x040273',
        }

        for m_key, m_val in default_message_info.items():
            if m_key not in guild_config['messages']:
                guild_config['messages'][m_key] = m_val

        for c_key, c_val in default_color_info.items():
            if c_key not in guild_config['colors']:
                guild_config['colors'][c_key] = c_val

        # TODO add default module enablement

        with open(self.config_file, 'w') as f:
            yaml.dump(self.configs, f, default_flow_style=False)

    def set_config(
            self,
            guild_id: int,
            group: str,
            key: str,
            value: str | int | bool,
            nested_value: str | int | bool | None = None,
    ):
        # Load the config for the guild if it doesn't exist in memory
        if str(guild_id) not in self.configs:
            self.load_config(guild_id)

        if group not in self.configs[str(guild_id)]:
            self.configs[str(guild_id)][group] = {}
        if key not in self.configs[str(guild_id)][group]:
            self.configs[str(guild_id)][group][key] = {}

        if nested_value:
            self.configs[str(guild_id)][group][key][value] = nested_value
        else:
            self.configs[str(guild_id)][group][key] = value

        # Write the updated config to the file
        with open(self.config_file, 'w') as f:
            yaml.dump(self.configs, f, default_flow_style=False)

    def get_message(
            self,
            guild_id: int,
            message_type: str,
    ) -> str:
        config = self.get_config(guild_id, 'messages')
        return config.get(message_type, '')

    def set_message(
            self,
            guild_id: int,
            message_type: str,
            message: str,
    ):
        self.set_config(guild_id, 'messages', message_type, message)

    def get_color(
            self,
            guild_id: int,
            color_type: str,
    ) -> int:
        config = self.get_config(guild_id, 'color')
        return config.get(color_type, 0x000000)

    def set_color(
            self,
            guild_id: int,
            color_type: str,
            color: int,
    ):
        self.set_config(guild_id, 'colors', color_type, color)

    def is_module_enabled(
            self,
            guild_id: int,
            module: str,
    ):
        config = self.get_config(guild_id, 'modules')
        return config.get(module, {}).get('enabled', True)

    def set_module_enabled(
            self,
            guild_id: int,
            module: str,
    ):
        state = self.is_module_enabled(guild_id, module)
        self.set_config(guild_id, 'modules', module, 'enabled', not state)
