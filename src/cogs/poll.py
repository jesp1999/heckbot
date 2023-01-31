from typing import List

import discord
from discord import Message, Embed
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

from bot import HeckBot
from src.service.config_service import ConfigService
from src.service.roll_service import RollService, RollRequest
from src.utils.chatutils import bold


class Poll(commands.Cog):
    """
    Cog for enabling polling-related features in the bot.
    """
    YES_NO_REACTIONS = ('👍', '👎')
    MULTI_CHOICE_REACTIONS = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣',
                              '7️⃣', '8️⃣', '9️⃣', '🔟')

    _roll_service: RollService = RollService()

    def __init__(
            self,
            bot: Bot
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: Bot = bot
        self._active_polls: List[Message] = []

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def poll(
            self,
            ctx: Context,
            *args
    ) -> None:
        """
        Polling command. The commander specifies the poll question and
        answers as space-delimited strings which may contain spaces as
        long as they are within quotes. If the commander only specifies
        the poll question, the answers will be assumed to be yes/no.
        :param ctx: Command context
        :param args: Command arguments, specifies the question and
        answers
        """
        if len(args) == 1:
            # Yes/no poll
            question: str = bold(args[0])
            message = await ctx.send(question)
            for reaction in self.YES_NO_REACTIONS:
                await message.add_reaction(reaction)
            # TODO enqueue poll results at a later time
        elif len(args) > 1:
            # Multi-choice poll
            question = bold(args[0])
            choices = args[1:]
            num_choices = len(args) - 1
            message_text = question
            for reaction, choice in zip(self.MULTI_CHOICE_REACTIONS, choices):
                message_text += f'\n{reaction}: {choice}'
            message = await ctx.send(message_text)
            # TODO handle more poll options than emojis in list
            for reaction in self.MULTI_CHOICE_REACTIONS[:num_choices]:
                await message.add_reaction(reaction)
            # TODO enqueue poll results at a later time
        else:
            await ctx.send('Incorrect syntax, try \"`!poll "<question>"'
                           ' "[choice1]" "[choice2]" ...`\"')

    async def close_poll(self, poll_message_id: int, poll_channel_id: int):
        channel = self._bot.get_channel(poll_channel_id)
        original_message = await channel.fetch_message(poll_message_id)
        poll_lines = original_message.content.split('\n')
        poll_title, poll_options = poll_lines[0], poll_lines[1:]
        poll_reactions = original_message.reactions
        parts = []
        for opt, rxn in zip(poll_options, poll_reactions):
            opt_rxn, opt_txt = opt.split(':')
            parts.append(f'{opt_txt}: {rxn.count}')
        embed = Embed(
            title=f'Results for poll: {poll_title}',
            description='\n'.join(parts)
        )
        await channel.send(embed=embed)

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def d(
            self,
            ctx: Context,
            num_sides: int = 6
    ) -> None:
        """
        Dice rolling command. The commander optionally specifies a
        number of sides to roll on a single dice. If no number is
        specified, a d6 will be rolled. The result will be formatted in
        an ascii table.
        :param ctx: Command context
        :param num_sides: Number of sides on the dice to be rolled
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(num=1, sides=num_sides)
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def d1(
            self,
            ctx: Context
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d1 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(num=1, sides=1)
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command(aliases=['flip', 'coinflip'])
    @commands.check(ConfigService.is_enabled)
    async def d2(
            self,
            ctx: Context
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d2 die / coin. The result will be formatted in
        an ascii table.
        :param ctx: Command context
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(num=1, sides=2)
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def d4(
            self,
            ctx: Context
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d4 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(num=1, sides=4)
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def d6(
            self,
            ctx: Context
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d6 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(
                    num=1,
                    sides=6
                )
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def d8(
            self,
            ctx: Context
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d8 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(num=1, sides=8)
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def d10(
            self,
            ctx: Context
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d10 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(num=1, sides=10)
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def d12(
            self,
            ctx: Context
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d12 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(num=1, sides=12)
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def d20(
            self,
            ctx: Context
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d20 die. The result will be
        formatted in an ascii table.
        :param ctx: Command context
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(num=1, sides=20)
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def d100(
            self,
            ctx: Context
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d100 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = self._roll_service.roll_many(
            [
                RollRequest(num=1, sides=100)
            ]
        )
        await ctx.send(self._roll_service.format_roll_results(roll_results))

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def roll(
            self,
            ctx: Context,
            *args
    ) -> None:
        """
        Dice rolling command. The commander specifies a series of
        comma-separated dice roll requests, in the following format:
        !roll 5d6 2d4 1d20  -> 5 d6s, 2 d4s, and 1 d20 will all be
        rolled.
        The results will be formatted in an ascii table.
        :param ctx: Command context
        :param args: Command arguments, specifies the number of dice and
        number of sides associated with each roll
        """
        if any([type(arg) is not str for arg in args]):
            return  # TODO give advice on how to reformat
        args: list[str]
        roll_requests = self._roll_service.parse_roll_requests(args)
        roll_results = self._roll_service.roll_many(roll_requests)
        await ctx.send(self._roll_service.format_roll_results(roll_results))


async def setup(
        bot: Bot
) -> None:
    """
    Setup function for registering the poll cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Poll(bot))
