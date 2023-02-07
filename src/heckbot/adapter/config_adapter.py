from __future__ import annotations

import os
from collections import defaultdict
from typing import Final
from typing import Literal
from typing import TypedDict

import yaml

DEFAULT_MODULE_BEHAVIOR: Final[bool] = True
ConfigGroup = Literal['messages', 'colors', 'modules']
ModuleConfig = TypedDict(
    'ModuleConfig', {
        'enabled': bool,
    },
)

GuildConfig = TypedDict(
    'GuildConfig', {
        'messages': defaultdict[str, str],
        'colors': defaultdict[str, int],
        'modules': defaultdict[str, ModuleConfig],
    },
)
DEFAULT_MESSAGE_INFO: Final[dict[str, str]] = {
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

DEFAULT_COLOR_INFO: Final[dict[str, int]] = {
    'embedColor': 0x040273,
}


class ConfigAdapter:
    def __init__(
            self,
    ) -> None:
        # guild_id -> group_name -> option -> value OR nested option
        self.configs: dict[str, GuildConfig] = {}
        self.config_file = os.getcwd() + '/../../../resources/config/config.yaml'

    @classmethod
    def get_default_guild_config(cls) -> GuildConfig:
        return {
            'messages': defaultdict(str),
            'colors': defaultdict(int),
            # Each module setting in a module defaults to the setting
            #  defined by DEFAULT_MODULE_BEHAVIOR
            'modules': defaultdict(
                lambda: {'enabled': DEFAULT_MODULE_BEHAVIOR},
            ),
        }

    def load_config(
            self,
            guild_id: int,
    ) -> None:
        # Load the config from the file
        data: dict[str, GuildConfig] = {}
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                data = yaml.safe_load(f)

        if str(guild_id) not in data:
            guild_config: GuildConfig = self.get_default_guild_config()
            data[str(guild_id)] = guild_config
        else:
            guild_config = data[str(guild_id)]

        # Generate default values if not present
        for m_key, m_val in DEFAULT_MESSAGE_INFO.items():
            guild_config['messages'][m_key] = m_val

        for c_key, c_val in DEFAULT_COLOR_INFO.items():
            guild_config['colors'][c_key] = c_val

        # TODO add default module enablement

        with open(self.config_file, 'w') as f:
            yaml.dump(self.configs, f, default_flow_style=False)

    def get_message(
            self,
            guild_id: int,
            message_type: str,
    ) -> str:
        if str(guild_id) not in self.configs:
            self.load_config(guild_id)
        return self.configs[str(guild_id)]['messages'][message_type]

    def set_message(
            self,
            guild_id: int,
            message_type: str,
            message: str,
    ) -> None:
        if str(guild_id) not in self.configs:
            self.load_config(guild_id)
        self.configs[str(guild_id)]['messages'][message_type] = message
        with open(self.config_file, 'w') as f:
            yaml.dump(self.configs, f, default_flow_style=False)

    def get_color(
            self,
            guild_id: int,
            color_type: str,
    ) -> int:
        if str(guild_id) not in self.configs:
            self.load_config(guild_id)
        return self.configs[str(guild_id)]['colors'][color_type]

    def set_color(
            self,
            guild_id: int,
            color_type: str,
            color: int,
    ) -> None:
        if str(guild_id) not in self.configs:
            self.load_config(guild_id)
        self.configs[str(guild_id)]['colors'][color_type] = color
        with open(self.config_file, 'w') as f:
            yaml.dump(self.configs, f, default_flow_style=False)

    def is_module_enabled(
            self,
            guild_id: int,
            module: str,
    ) -> bool:
        if str(guild_id) not in self.configs:
            self.load_config(guild_id)
        return self.configs[str(guild_id)]['modules'][module]['enabled']

    def set_module_enabled(
            self,
            guild_id: int,
            module: str,
    ) -> None:
        if str(guild_id) not in self.configs:
            self.load_config(guild_id)
        state = self.is_module_enabled(guild_id, module)
        self.configs[str(guild_id)]['modules'][module]['enabled'] = not state
        with open(self.config_file, 'w') as f:
            yaml.dump(self.configs, f, default_flow_style=False)
