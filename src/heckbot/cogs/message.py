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

    @commands.command(aliases=['message', 'addresponse', 'respond'])
    async def msg(
            self,
            ctx: Context[Bot],
            subcommand: str,
            pattern: str | None = None,
            *message_parts: str,
    ) -> None:
        """
        General purpose message-matching root command. Aliases the
        functionality of all other message-matching commands by using
        the subcommand parameter to select which function to perform.
        :param ctx: Command context
        :param subcommand: Sub-command of the message function call
        :param pattern: Pattern string to match with the reaction
        :param message_parts: Parts of the message to respond with
        :return:
        """
        message = ' '.join(message_parts)
        if subcommand == 'add':
            if isinstance(pattern, str) and isinstance(message, str):
                await self.madd(ctx, pattern, message)
        elif subcommand in ['remove', 'delete', 'rm', 'del']:
            if isinstance(pattern, str):
                await self.mdel(ctx, pattern, message)
        # elif subcommand in ['list', 'lst']:
        #     await self.mlist(ctx, pattern)

    @commands.command(aliases=['messageadd', 'msgadd', 'madd'])
    async def message_add(
            self,
            ctx: Context[Bot],
            pattern: str,
            message: str,
    ) -> None:
        """
        Reaction association command. Creates an association between a
        pattern and message such that any messages which contain the
        specified pattern will be responded to with the specified
        message, permission permitting.
        :param ctx: Command context
        :param pattern: Pattern string to match with the message
        :param message: Message to respond with
        """
        await self.madd(ctx, pattern, message)

    @commands.command(
        aliases=[
            'messagedelete', 'mdel', 'msgdel', 'msgremove', 'messageremove',
            'rsgrem', 'mrem',
        ],
    )
    async def message_delete(
            self,
            ctx: Context[Bot],
            pattern: str,
            message: str | None = None,
    ) -> None:
        """
        Message dissociation command. Removes an association between a
        pattern and message. If no message is specified, the bot will
        remove all associations with the specified pattern.

        See the documentation for the associate command for what an
        association represents.
        :param ctx: Command context
        :param pattern: Pattern string to remove associations from
        :param message: Message to (no longer) respond with
        """
        await self.mdel(ctx, pattern, message)

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

    async def madd(
            self,
            ctx: Context[Bot],
            pattern: str,
            message: str,
    ) -> None:
        if ctx.guild is None:
            return
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

    async def mdel(
            self,
            ctx: Context[Bot],
            pattern: str,
            message: str | None = None,
    ) -> None:
        if ctx.guild is None:
            return
        if message is None:
            self._message_table.remove_all_messages(
                str(ctx.guild.id),
                pattern,
            )
            await ctx.send(
                f'Successfully dissociated the keyword '
                f'\"{pattern}\" from all messages!',
            )
        else:
            self._message_table.remove_message(
                str(ctx.guild.id),
                pattern,
                message,
            )
            await ctx.send(
                f'Successfully dissociated the keyword '
                f'\"{pattern}\" with the message '
                f'\"{message}\"!',
            )


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the message cog
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Message(bot))
