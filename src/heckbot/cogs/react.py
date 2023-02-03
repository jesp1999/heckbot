from __future__ import annotations

import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from heckbot.adaptor.dynamo_table_adaptor import DynamoTableAdaptor

from bot import HeckBot


class React(commands.Cog):
    """
    Cog for enabling reaction-matching-related features in the bot.
    """

    _association_table: DynamoTableAdaptor = DynamoTableAdaptor(
        table_name='HeckBotAssociations',
        pk_name='Server',
        sk_name='Pattern',
    )

    def __init__(
            self,
            bot: HeckBot,
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: HeckBot = bot

    def get_all_associations(
            self,
            guild: str,
    ) -> dict[str, list[str]]:
        """
        Gets all text-pattern-to-emoji mappings for a given guild.
        :param guild: Identifier for the guild
        :return: Mapping of text patterns to lists of associated emojis
        in order
        """
        results: list[dict[str, list[str]]] = self._association_table.read(
            pk_value=guild,
        )

        associations: dict[str, list[str]] = {
            result['Pattern']: result['Reactions']
            for result in results
        }
        return associations

    def get_associations_for_pattern(
            self,
            guild: str,
            pattern: str,
    ) -> list[str]:
        """
        Gets all emojis associated with a given guild and text-pattern
        for a given guild.
        :param guild: Identifier for the guild
        :param pattern: Text pattern
        :return: List of associated emojis in order
        """
        associations: list[dict[str, list[str]]] = (
            self._association_table.read(
                pk_value=guild,
                sk_value=pattern,
            )
        )
        return associations[0]['Reactions']

    def add_association(
            self,
            guild: str,
            pattern: str,
            reaction: str,
    ) -> None:
        """
        Adds a text-pattern-to-emoji association for a given guild.
        :param guild: Identifier for the guild
        :param pattern: Text pattern
        :param reaction: Emoji to be reacted
        """
        self._association_table.add_list_item(
            pk_value=guild, sk_value=pattern,
            list_name='Reactions',
            item=reaction,
        )

    def remove_association(
            self,
            guild: str,
            pattern: str,
            reaction: str | None = None,
    ) -> None:
        """
        Removes all emoji associations to a given text-pattern for a
        given guild.
        :param guild: Identifier for the guild
        :param pattern: Text pattern
        :param reaction: Emoji to be reacted
        """
        if reaction is None:
            self._association_table.delete(
                pk_value=guild,
                sk_value=pattern,
            )
        else:
            self._association_table.remove_list_item(
                pk_value=guild, sk_value=pattern,
                list_name='Reactions', item=reaction,
            )

    @commands.command()
    async def react(
            self,
            ctx: Context[Bot],
            subcommand: str,
            pattern: str | None = None,
            reaction: str | None = None,
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
    async def react_add(
            self,
            ctx: Context[Bot],
            pattern: str,
            reaction: str,
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

    @commands.command(
        aliases=[
            'reactdelete', 'dissociate', 'dissoc',
            'rdel', 'reactdel', 'reactremove',
            'reactrem', 'rrem',
        ],
    )
    async def react_delete(
            self,
            ctx: Context[Bot],
            pattern: str,
            reaction: str | None = None,
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
    async def disassociate(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Joke command based on a misspelling of the dissociate command.
        Directs the commander sarcastically in the right direction!
        """
        await ctx.send('The command is \"`!dissociate`\", y\'know 😉')

    @commands.command(
        aliases=[
            'reactlist', 'listassociations', 'rlist',
            'rlst',
        ],
    )
    async def react_list(
            self,
            ctx: Context[Bot],
            pattern: str | None = None,
    ) -> None:
        if ctx.guild is not None:
            await self.rlist(ctx, pattern, ctx.guild.id)

    @commands.Cog.listener('on_message')
    async def on_message(
            self,
            message: discord.Message,
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
        if guild is None:
            return

        associations = self.get_all_associations(
            str(guild.id),
        )
        for word, emojis in associations.items():
            if word in text:
                for emoji in emojis:
                    asyncio.get_event_loop().create_task(
                        message.add_reaction(emoji),
                    )

    async def radd(
            self,
            ctx,
            pattern,
            reaction,
    ):
        self.add_association(
            str(ctx.guild.id),
            pattern,
            reaction,
        )
        await ctx.send(
            f'Successfully associated the keyword '
            f'\"{pattern}\" with the reaction '
            f'\"{reaction}\"!',
        )

    async def rdel(
            self,
            ctx,
            pattern,
            reaction,
    ):
        if reaction is None:
            self.remove_association(
                str(ctx.guild.id),
                pattern,
            )
            await ctx.send(
                f'Successfully dissociated the keyword '
                f'\"{pattern}\" from all reactions!',
            )
        else:
            self.remove_association(
                str(ctx.guild.id),
                pattern,
                reaction,
            )
            await ctx.send(
                f'Successfully dissociated the keyword '
                f'\"{pattern}\" with the reaction '
                f'\"{reaction}\"!',
            )

    async def rlist(
            self,
            ctx,
            pattern,
            guild_id,
    ):
        if pattern:
            associations: str = str(
                self.get_associations_for_pattern(
                    guild=str(guild_id),
                    pattern=pattern,
                ),
            )
        else:
            associations = str(
                self.get_all_associations(
                    guild=str(ctx.guild.id),
                ),
            )
        await ctx.send(associations)


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the react-match cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(React(bot))
