import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot

from src.service.association_service import AssociationService


class ReactMatch(commands.Cog):
    """
    Cog for enabling reaction-matching-related features in the bot.
    """
    _association_handler: AssociationService = AssociationService()

    def __init__(self, bot: Bot) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: Bot = bot

    @commands.command()
    async def associate(
            self,
            ctx: Context,
            pattern: str,
            reaction: str
    ) -> None:
        """
        Reaction association command. Creates an association between a
        pattern and reaction such that any messages which contain the
        specified pattern will be reacted with the specified reaction,
        permission permitting.
        :param ctx: Command context
        :param pattern: Pattern string to match with the reaction
        :param reaction: Reaction to respond with
        """
        self._association_handler.add_association(
            str(ctx.guild.id),
            pattern,
            reaction
        )
        await ctx.send(f'Successfully associated the keyword '
                       f'\"{pattern}\" with the reaction '
                       f'\"{reaction}\"!')

    @commands.command()
    async def dissociate(
            self,
            ctx: Context,
            pattern: str,
            reaction: str = ''
    ) -> None:
        """
        Reaction dissociation command. Removes an association between a
        pattern and reaction. If no reaction is specified, the bot will
        remove all associations with the specified pattern.

        See the documentation for the associate command for what an
        association represents.
        :param ctx: Command context
        :param pattern: Pattern string to remove associations from
        :param reaction: Reaction to (no longer) respond with
        """
        if reaction == '':
            self._association_handler.remove_association(
                str(ctx.guild.id),
                pattern
            )
            await ctx.send(f'Successfully dissociated the keyword '
                           f'\"{pattern}\" from all reactions!')
        else:
            self._association_handler.remove_association(
                str(ctx.guild.id),
                pattern,
                reaction
            )
            await ctx.send(f'Successfully dissociated the keyword '
                           f'\"{pattern}\" with the reaction '
                           f'\"{reaction}\"!')

    @commands.command()
    async def disassociate(
            self,
            ctx: Context
    ) -> None:
        """
        Joke command based on a misspelling of the dissociate command.
        Directs the commander sarcastically in the right direction!
        """
        await ctx.send('The command is \"`!dissociate`\", y\'know 😉')

    @commands.Cog.listener('on_message')
    async def on_message(self, message: discord.Message) -> None:
        """
        Event listener triggered whenever the bot detects a message.
        This listener will attempt to match the text contents of the
        given message with all registered reaction associations to react
        all appropriate reactions based on the contents of the message.
        :param message: The Discord message to be analyzed
        """
        if message.author.bot or (
                await self._bot.get_context(message)
        ).valid:
            return

        text = message.content.lower()
        server = message.guild

        associations = self._association_handler.get_all_associations(
            str(server.id)
        )
        for word, emojis in associations.items():
            if word in text:
                for emoji in emojis:
                    asyncio.get_event_loop().create_task(
                        message.add_reaction(emoji)
                    )


async def setup(bot: Bot) -> None:
    """
    Setup function for registering the react-match cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(ReactMatch(bot))
