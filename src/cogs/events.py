import discord
from discord.ext import commands
from discord.ext.commands import Bot

from src.types.constants import (PRIMARY_GUILD_ID, WELCOME_CHANNEL_ID,
                                 WELCOME_MESSAGE, EMBED_COLOR, GUILD_JOIN_TITLE,
                                 GUILD_JOIN_DESCRIPTION)


class Events(commands.Cog):
    def __init__(
            self,
            bot: Bot
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: Bot = bot

    @commands.Cog.listener()
    async def on_member_join(
            self,
            member: discord.Member
    ) -> None:
        """
        Event listener triggered when the bot detects a new member
        joining the guild. Sends a message in whitelisted guilds with
        a designated welcome channel to welcome the user to the guild.
        :param member: Discord member who joined
        """
        if member.guild.id == PRIMARY_GUILD_ID:
            channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
            await channel.send(WELCOME_MESSAGE.format(member.id))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        welcome_channel = guild.system_channel

        embed = discord.Embed(
            color=EMBED_COLOR,
            title=GUILD_JOIN_TITLE,
            description=GUILD_JOIN_DESCRIPTION
        )

        if welcome_channel is not None:
            await welcome_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        pass


async def setup(
        bot: Bot
) -> None:
    """
    Setup function for registering the poll cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Events(bot))
