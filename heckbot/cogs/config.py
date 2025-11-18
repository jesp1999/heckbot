from __future__ import annotations

from typing import Literal

from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from heckbot.adapter.config_adapter import ConfigAdapter

from bot import HeckBot

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
            bot: HeckBot,
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot = bot
        self._config_adapter = ConfigAdapter()

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
            *config_options,
    ) -> None:
        raise NotImplementedError


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the config cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Config(bot))
