import os

import aiohttp
from discord.ext import commands
from discord.ext.commands import Bot, Context


class Config(commands.Cog):
    """
    Cog for config-related features in the bot.
    """

    def __init__(
            self,
            bot: Bot
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: Bot = bot

    @commands.command()
    async def hbconf(
            self,
            ctx: Context,
            config_option: str,
            config_value: str
    ) -> None:
        pass


async def setup(
        bot: Bot
):
    """
    Setup function for registering the gif cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Config(bot))
