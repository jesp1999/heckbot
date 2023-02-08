from __future__ import annotations

import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from heckbot.adapter.message_table_adapter import MessageTableAdapter

from bot import HeckBot


class Message(commands.Cog):
    """
    Cog for enabling message responses
    """

    _message_table: MessageTableAdapter = MessageTableAdapter()

    def __init__(
            self,
            bot: HeckBot,
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot = bot

    @commands.command()
    async def msg(
            self,
            ctx: Context[Bot],
            pattern: str,
            *message_parts
    ) -> None:
        """
        Message association command. Creates the association between a
        pattern and a reaction message such that any messages which
        contain the specified pattern will be responded to with the
        reaction message, permission permitting.

        :param ctx: Command context
        :param pattern: Key used for parsing messages
        :param message_parts: parts of the desired message to be sent
        """
        if ctx.guild is None:
            return
        message = ' '.join(message_parts)
        self._message_table.add_message(
            str(ctx.guild.id),
            pattern,
            message,
        )
        await ctx.send(
            f'Successfully associated the keyword '
            f'\"{pattern}\" with the message '
            f'\"{message}\"!',
        )

    @commands.Cog.listener('on_message')
    async def on_message(
            self,
            message: discord.Message,
    ) -> None:
        """
        Event listener triggered whenever the bot detects a message.
        This listener will attempt to match the text contents of the
        given message with all registered reaction associations to
        respond with all appropriate messages based on the contents of
        the message.
        :param message: The Discord message to be analyzed
        """
        if message.author.bot or (
                await self._bot.get_context(message)
        ).valid:
            return

        text = message.content.lower()
        guild = message.guild
        if guild is None:
            return

        associations = self._message_table.get_all_messages(
            str(guild.id),
        )
        for word, responses in associations.items():
            if word in text:
                for response in responses:
                    asyncio.get_event_loop().create_task(
                        (await self._bot.get_context(message)).send(response),
                    )


async def setup(
        bot: HeckBot,
):
    """
    Setup function for registering the message cog
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Message(bot))
