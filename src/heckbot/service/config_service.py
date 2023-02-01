from __future__ import annotations

from discord.ext.commands import Bot
from discord.ext.commands import Context
from heckbot.adaptor.config_json_adaptor import ConfigJsonAdaptor
from heckbot.types.types import JsonObject


class ConfigService:
    _config_adaptor: ConfigJsonAdaptor = ConfigJsonAdaptor()

    @classmethod
    def set_config_option(
            cls,
            guild_id: str,
            *setting_parts
    ) -> None:
        return cls._config_adaptor.save(guild_id, setting_parts)

    @classmethod
    def get_config_option(
            cls,
            guild_id: str,
            *setting_parts
    ) -> JsonObject:
        return cls._config_adaptor.load(guild_id, *setting_parts)

    @classmethod
    def generate_default_config(
            cls,
            bot: Bot,
            guild_id: str,
    ):
        # Module enablement
        command_info = {(cmd.name, cmd.cog_name) for cmd in bot.commands}
        disabled_by_default = []
        for command_name, module_name in command_info:
            enabled = command_name not in disabled_by_default
            cls._config_adaptor.save(
                guild_id,
                'modules',
                module_name,
                'commands',
                command_name,
                'enabled',
                'true' if enabled else 'false',
            )

        # Messages
        message_info = {
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
        for message_type, message in message_info.items():
            cls._config_adaptor.save(
                guild_id,
                'messages',
                message_type,
                message,
            )

        # Bot information
        bot_info = {
            'botCustomStatus': 'the part :)',
        }
        for bot_info_type, bot_info in bot_info.items():
            cls._config_adaptor.save(
                guild_id,
                'botInfo',
                bot_info_type,
                bot_info,
            )

        # Colors
        color_info = {
            'embedColor': '0x040273',
        }
        for color_type, color in color_info.items():
            cls._config_adaptor.save(
                guild_id,
                'colors',
                color_type,
                color,
            )

    @classmethod
    def is_enabled(cls, ctx: Context[Bot]):
        return cls._config_adaptor.load(
            str(ctx.guild.id),
            'modules',
            ctx.command.cog_name,
            'commands',
            ctx.command.name,
            'enabled',
        ) == 'true'
