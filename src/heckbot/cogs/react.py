import asyncio
from typing import Optional

import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot

from heckbot.service.config_service import ConfigService
from heckbot.service.react_service import AssociationService


class React(commands.Cog):
    """
    Cog for enabling reaction-matching-related features in the bot.
    """
    _association_service: AssociationService = AssociationService()

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
    @commands.check(ConfigService.is_enabled)
    async def react(
            self,
            ctx: Context[Bot],
            subcommand: str,
            pattern: Optional[str] = None,
            reaction: Optional[str] = None
    ) -> None:
        """
        General purpose reaction-matching root command. Aliases the
        functionality of all other reaction-matching commands by using
        the subcommand parameter to select which function to perform.
        :param ctx:
        :param subcommand:
        :param pattern:
        :param reaction:
        :return:
        """
        if subcommand == 'add':
            await self.radd(ctx, pattern, reaction)
        elif subcommand in ['remove', 'delete', 'rm', 'del']:
            await self.rdel(ctx, pattern, reaction)
        elif subcommand in ['list', 'lst']:
            await self.rlist(ctx, pattern, reaction)

    @commands.command(aliases=['reactadd', 'associate', 'assoc', 'radd'])
    @commands.check(ConfigService.is_enabled)
    async def react_add(
            self,
            ctx: Context[Bot],
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
        await self.radd(ctx, pattern, reaction)

    @commands.command(aliases=['reactdelete', 'dissociate', 'dissoc',
                               'rdel', 'reactdel', 'reactremove',
                               'reactrem', 'rrem'])
    @commands.check(ConfigService.is_enabled)
    async def react_delete(
            self,
            ctx: Context[Bot],
            pattern: str,
            reaction: Optional[str] = None
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
        await self.rdel(ctx, pattern, reaction)

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def disassociate(
            self,
            ctx: Context[Bot]
    ) -> None:
        """
        Joke command based on a misspelling of the dissociate command.
        Directs the commander sarcastically in the right direction!
        """
        await ctx.send('The command is \"`!dissociate`\", y\'know 😉')

    @commands.command(aliases=['reactlist', 'listassociations', 'rlist',
                               'rlst'])
    @commands.check(ConfigService.is_enabled)
    async def react_list(
            self,
            ctx: Context[Bot],
            pattern: Optional[str] = None
    ) -> None:
        await self.rlist(ctx, pattern, ctx.guild.id)

    @commands.Cog.listener('on_message')
    async def on_message(
            self,
            message: discord.Message
    ) -> None:
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
        guild = message.guild

        associations = self._association_service.get_all_associations(
            str(guild.id)
        )
        for word, emojis in associations.items():
            if word in text:
                for emoji in emojis:
                    asyncio.get_event_loop().create_task(
                        message.add_reaction(emoji)
                    )

    async def radd(self, ctx, pattern, reaction):
        self._association_service.add_association(
            str(ctx.guild.id),
            pattern,
            reaction
        )
        await ctx.send(f'Successfully associated the keyword '
                       f'\"{pattern}\" with the reaction '
                       f'\"{reaction}\"!')

    async def rdel(self, ctx, pattern, reaction):
        if reaction is None:
            self._association_service.remove_association(
                str(ctx.guild.id),
                pattern
            )
            await ctx.send(f'Successfully dissociated the keyword '
                           f'\"{pattern}\" from all reactions!')
        else:
            self._association_service.remove_association(
                str(ctx.guild.id),
                pattern,
                reaction
            )
            await ctx.send(f'Successfully dissociated the keyword '
                           f'\"{pattern}\" with the reaction '
                           f'\"{reaction}\"!')

    async def rlist(self, ctx, pattern, guild_id):
        if pattern:
            associations = (
                self._association_service.get_associations_for_pattern(
                    guild=str(guild_id),
                    pattern=pattern
                )
            )
        else:
            associations = self._association_service.get_all_associations(
                guild=str(ctx.guild.id)
            )
        await ctx.send(str(associations))


async def setup(
        bot: Bot
) -> None:
    """
    Setup function for registering the react-match cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(React(bot))
