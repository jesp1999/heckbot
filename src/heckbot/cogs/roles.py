from __future__ import annotations

import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from heckbot.adapter.reaction_table_adapter import ReactionTableAdapter

from bot import HeckBot


class Roles(commands.Cog):
    """
    Cog for enabling role-selection related features in the bot.
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

    @commands.command(aliases=['createrolesmessage', 'createrolesmsg'])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def create_roles_message(self, ctx: Context):
        """
        Sends a role-reaction-enabled message in the current chat.
        :param ctx: Context of the command
        """
        await ctx.author.send(f'{ctx.guild.roles}')


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the react-match cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Roles(bot))
