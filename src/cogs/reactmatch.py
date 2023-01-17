import asyncio

import discord
from discord.ext import commands
from discord.ext.commands import Context, Bot

from src.handler.association_handler import AssociationHandler


class ReactMatch(commands.Cog):
    _association_handler: AssociationHandler = AssociationHandler()

    def __init__(self, bot: Bot):
        self._bot: Bot = bot

    @commands.command()
    async def associate(self, ctx: Context, *args):
        if len(args) != 2:
            await ctx.send('Incorrect syntax, try \"`!associate <word> <emoji>`\"')
        else:
            word = args[0].lower()
            emoji = args[1]
            self._association_handler.add_association(str(ctx.guild.id), word, emoji)
            await ctx.send(f'Successfully associated the keyword \"{word}\" with the reaction \"{emoji}\"!')

    @commands.command()
    async def dissociate(self, ctx: Context, *args):
        if len(args) == 1:
            word = args[0].lower()
            self._association_handler.remove_association(str(ctx.guild.id), word)
            await ctx.send(f'Successfully dissociated the keyword \"{word}\" from all reactions!')
        elif len(args) == 2:
            word = args[0].lower()
            emoji = args[1]
            self._association_handler.remove_association(str(ctx.guild.id), word, emoji)
            await ctx.send(f'Successfully dissociated the keyword \"{word}\" with the reaction \"{emoji}\"!')
        else:
            await ctx.send('Incorrect syntax, try \"`!dissociate <word>`\"')

    @commands.command()
    async def disassociate(self, ctx: Context):
        await ctx.send('The command is \"`!dissociate`\", y\'know 😉')

    @commands.Cog.listener('on_message')
    async def on_message(self, message: discord.Message):
        if message.author.bot or (await self._bot.get_context(message)).valid:
            return

        text = message.content.lower()
        server = message.guild

        associations = self._association_handler.get_all_associations(str(server.id))
        for word, emojis in associations.items():
            if word in text:
                for emoji in emojis:
                    asyncio.get_event_loop().create_task(message.add_reaction(emoji))


async def setup(bot: Bot):
    await bot.add_cog(ReactMatch(bot))
