import random

from discord.ext import commands
from discord.ext.commands import Bot, Context

from src.service.roll_service import RollService, RollRequest


class Poll(commands.Cog):
    _roll_service: RollService = RollService()
    _yes_no_reactions = ['👍', '👎']
    _multi_choice_reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    def __init__(self, bot: Bot):
        self._bot: Bot = bot

    @commands.command()
    async def poll(self, ctx: Context, *args):
        if len(args) == 1:
            # Yes/no poll
            question = args[0]
            if question[:2] != '**' or question[-2:] != '**':
                question = '**' + question + '**'

            message = await ctx.send(question)
            for reaction in self._yes_no_reactions:
                await message.add_reaction(reaction)
        elif len(args) > 1:
            # Multi-choice poll
            question = args[0]
            choices = args[1:]
            if question[:2] != '**' or question[-2:] != '**':
                question = '**' + question + '**'
            num_choices = len(args) - 1
            message_text = question
            for i in range(num_choices):
                message_text += f'\n{self._multi_choice_reactions[i]}: {choices[i]}'
            message = await ctx.send(message_text)
            # TODO handle more poll options than emojis in list
            for reaction in self._multi_choice_reactions[:num_choices]:
                await message.add_reaction(reaction)
        else:
            await ctx.send('Incorrect syntax, try \"`!poll "<question>" "[choice1]" "[choice2]" ...`\"')

    @commands.command()
    async def d(self, ctx: Context, num_sides: int = 6):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=num_sides)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    async def d1(self, ctx: Context):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=1)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command(aliases=['flip', 'coinflip'])
    async def d2(self, ctx: Context):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=2)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    async def d4(self, ctx: Context):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=4)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    async def d6(self, ctx: Context):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=6)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    async def d8(self, ctx: Context):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=8)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    async def d10(self, ctx: Context):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=10)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    async def d12(self, ctx: Context):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=12)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    async def d20(self, ctx: Context):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=20)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    async def d100(self, ctx: Context):
        roll_results = self._roll_service.roll_many([RollRequest(num=1, sides=100)])
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    async def roll(self, ctx: Context, *args):
        if any([type(arg) is not str for arg in args]):
            return  # TODO give advice on how to reformat
        args: list[str]
        roll_requests = self._roll_service.parse_roll_requests(args)
        roll_results = self._roll_service.roll_many(roll_requests)
        await ctx.send(self._roll_service.format_roll_results(roll_results))


async def setup(bot: Bot):
    await bot.add_cog(Poll(bot))
