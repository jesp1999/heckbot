from __future__ import annotations

import discord
from discord import TextChannel
from discord.ext import commands
from heckbot.types.constants import PRIMARY_GUILD_ID
from heckbot.types.constants import WELCOME_CHANNEL_ID

from bot import HeckBot


class Events(commands.Cog):
    def __init__(
            self,
            bot: HeckBot,
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot = bot

    @commands.Cog.listener()
    async def on_member_join(
            self,
            member: discord.Member,
    ) -> None:
        """
        Event listener triggered when the bot detects a new member
        joining the guild. Sends a message in whitelisted guilds with
        a designated welcome channel to welcome the user to the guild.
        :param member: Discord member who joined
        """
        if member.guild.id == PRIMARY_GUILD_ID:
            channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
            if isinstance(channel, TextChannel):
                await channel.send(
                    self._bot.config.get_message(
                        member.guild.id,
                        'welcomeMessage',
                    ).format(member.id),
                )

    @commands.Cog.listener()
    async def on_guild_join(
            self,
            guild,
    ):
        welcome_channel = guild.system_channel

        embed = discord.Embed(
            color=self._bot.config.get_color(guild.id, 'embedColor'),
            title=self._bot.config.get_message(
                guild.id,
                'guildJoinMessageTitle',
            ),
            description=self._bot.config.get_message(
                guild.id,
                'guildJoinMessage',
            ),
        )

        if welcome_channel is not None:
            await welcome_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # TODO implement some cleanup here, maybe remove guild resources
        #  from DB and configs?
        pass


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the events cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Events(bot))
