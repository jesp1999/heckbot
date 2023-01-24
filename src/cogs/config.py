from functools import wraps
from typing import Optional, Literal, Any

from discord.ext import commands
from discord.ext.commands import Bot, Context,Command

from src.adaptor.config_json_adaptor import ConfigJsonAdaptor

ConfigCommand = Literal[
    'add', 'create', 'update', 'set', 'remove', 'unset',
    'delete', 'get', 'read', 'load', 'list'
]


class Config(commands.Cog):
    """
    Cog for config-related features in the bot.
    """
    config_adaptor = ConfigJsonAdaptor()

    def __init__(
            self,
            bot: Bot
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: Bot = bot
        self._current_config: dict = {}

    @commands.command(aliases=['config', 'conf', 'heckbotconf',
                               'heckbotconfig'])
    # @commands.check(is_enabled)
    async def hbconf(
            self,
            ctx: Context,
            command: ConfigCommand,
            *config_options
    ) -> None:
        if command in ['add', 'create']:
            self.config_adaptor.save(
                str(ctx.guild.id),
                *config_options
            )
            self._current_config = self.config_adaptor.load(
                str(ctx.guild.id)
            )
        elif command in ['update', 'set']:
            self.config_adaptor.save(
                str(ctx.guild.id),
                *config_options
            )
            self._current_config = self.config_adaptor.load(
                str(ctx.guild.id)
            )
        elif command in ['remove', 'unset', 'delete']:
            self.config_adaptor.save(
                str(ctx.guild.id),
                *config_options,
                None
            )
            self._current_config = self.config_adaptor.load(
                str(ctx.guild.id)
            )
        elif command in ['get', 'read', 'load']:
            self._current_config = self.config_adaptor.load(
                str(ctx.guild.id),
                *config_options
            )
            await ctx.send(str(self._current_config))
        elif command == 'list':
            self._current_config = self.config_adaptor.load(
                str(ctx.guild.id),
                *config_options
            )
            await ctx.send(str(self._current_config))


def is_enabled(ctx: Context):
    print(dir(ctx.command))
    a = Config.config_adaptor.load(
        str(ctx.guild.id),
        'modules',
        ctx.command.name,
        'enabled'
    ) not in ('false', 'FALSE', 'f', 'F', 'n', 'N', 'no', 'NO', 0, '0')
    print(a)
    return a


async def setup(
        bot: Bot
):
    """
    Setup function for registering the gif cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Config(bot))
