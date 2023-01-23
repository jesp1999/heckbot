import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Bot, Context


class Message(commands.Cog):
    """
    Cog for enabling message responses
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
        self._associations = {}

    @commands.command()
    async def msg(
            self,
            _: Context,
            pattern: str,
            *message_parts
    ) -> None:
        """
        Message response command. Takes in message parameters and sends
        a message in the same channel
        :param pattern: Key used for parsing messages
        :param _: Command context
        :param message_parts: parts of the desired message to be sent
        """
        message = ' '.join(message_parts)
        self._associations[pattern] = message

    @commands.Cog.listener('on_message')
    async def on_message(
            self,
            message: discord.Message
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

        for word, msg in self._associations.items():
            if word in text:
                asyncio.get_event_loop().create_task(
                    (await self._bot.get_context(message)).send(msg)
                )


async def setup(
        bot: Bot
):
    """
    Setup function for registering the message cog
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Message(bot))
