from __future__ import annotations

from typing import Literal

from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from heckbot.adaptor.config_adaptor import ConfigAdaptor as ConfigAdaptor

ConfigCommand = Literal[
    'add', 'create', 'update', 'set', 'remove', 'unset',
    'delete', 'get', 'read', 'load', 'list',
]


class Config(commands.Cog):
    """
    Cog for config-related features in the bot.
    """

    def __init__(
            self,
            bot: Bot,
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: Bot = bot
        self._config_adaptor = ConfigAdaptor()

    @commands.command(
        aliases=[
            'config', 'conf', 'heckbotconf',
            'heckbotconfig',
        ],
    )
    async def hbconf(
            self,
            ctx: Context[Bot],
            command: ConfigCommand,
            *config_options
    ) -> None:
        raise NotImplementedError


async def setup(
        bot: Bot,
) -> None:
    """
    Setup function for registering the gif cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Config(bot))
