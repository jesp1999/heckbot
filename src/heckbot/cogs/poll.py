from __future__ import annotations

import random
from collections import namedtuple
from datetime import datetime
from datetime import timedelta
from typing import Sequence

from discord import Forbidden
from discord import Message
from discord import TextChannel
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from heckbot.utils.chatutils import bold
from heckbot.utils.chatutils import codeblock
from table2ascii import PresetStyle
from table2ascii import table2ascii
from table2ascii import TableStyle

from bot import cursor
from bot import db_conn
from bot import HeckBot

Bounds: namedtuple = namedtuple(
    'Bounds',
    ['min', 'max'],
)
RESULT_DICE_LENGTH_BOUNDS: Bounds = Bounds(6, 9)
RESULT_ROLLS_LENGTH_BOUNDS: Bounds = Bounds(7, 21)
RESULT_SUM_LENGTH_BOUNDS: Bounds = Bounds(5, 8)

RollRequest: namedtuple = namedtuple(
    'RollRequest',
    ['num', 'sides'],
    defaults=(1, 6),
)
RollResult: namedtuple = namedtuple(
    'RollResult',
    ['dice', 'rolls'],
)


class Poll(commands.Cog):
    """
    Cog for enabling polling-related features in the bot.
    """
    YES_NO_REACTIONS = ('👍', '👎')
    MULTI_CHOICE_REACTIONS = (
        '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣',
        '7️⃣', '8️⃣', '9️⃣', '🔟',
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
        self._db_conn = db_conn
        self._cursor = cursor

    @staticmethod
    def roll_many(
            roll_requests: Sequence[RollRequest],
    ) -> Sequence[RollResult]:
        """
        Simulates the rolling of a set of dice according to an input
        list of RollRequests.
        :param roll_requests: RollRequests which specify the rolling
        parameters
        :return: results of the dice rolls as RollResult objects
        """
        roll_results = []
        for roll_request in roll_requests:
            rolls = []
            for roll in range(roll_request.num):
                rolls.append(random.randint(1, roll_request.sides))
            roll_results.append(
                RollResult(
                    dice=f'{roll_request.num}D{roll_request.sides}',
                    rolls=rolls,
                ),
            )
        return roll_results

    @staticmethod
    def parse_roll_requests(
            roll_requests: Sequence[str],
    ) -> Sequence[RollRequest]:
        """
        Parses raw roll requests from command args into the RoleRequest
        data type.
        :param roll_requests: Raw roll requests from command args
        :return: Roll requests as RoleRequest data types
        """
        parsed_roll_requests = []
        for roll_request in roll_requests:
            num_str, _, sides_str = roll_request.lower().partition('d')
            num = int(num_str) if num_str.isdigit() else 1
            sides = int(sides_str) if sides_str.isdigit() else 6
            parsed_roll_requests.append(
                RollRequest(
                    num=num, sides=sides,
                ),
            )
        return parsed_roll_requests

    @staticmethod
    def get_rolls_pretty(
            rolls: list[int],
            line_length: int = RESULT_ROLLS_LENGTH_BOUNDS.max,
    ) -> str:
        """
        Format the rolls of a roll command to span multiple lines as to
        not exceed the specified line_length.
        :param rolls: Rolls of a roll command, as ints
        :param line_length: Maximum length of a line
        :return: Formatted rolls
        """
        rolls_pretty = []
        roll_pretty = str(rolls[0])
        for roll in rolls[1:]:
            # +3 accounts for padding and the space between the rolls
            if len(roll_pretty) + 3 + len(str(roll)) > line_length:
                rolls_pretty.append(roll_pretty)
                roll_pretty = str(roll)
            else:
                roll_pretty += ' ' + str(roll)
        rolls_pretty.append(roll_pretty)
        return '\n'.join(rolls_pretty)

    @staticmethod
    def format_roll_results(
            roll_results: Sequence[RollResult],
            table_style: TableStyle = PresetStyle.double_thin_box,
    ) -> str:
        """
        Format results of a roll command into an ascii table with
        line-wrapping.
        :param roll_results:
        :param table_style: Table style in table2ascii format
        :return: results of a roll command as an ascii table
        """
        table_body = []
        max_dice_strlen = RESULT_DICE_LENGTH_BOUNDS.min
        max_rolls_strlen = RESULT_ROLLS_LENGTH_BOUNDS.min
        max_sum_strlen = RESULT_SUM_LENGTH_BOUNDS.min
        for i, rr in enumerate(roll_results):
            rr_pretty = Poll.get_rolls_pretty(rr.rolls)
            # If more than one line, rolls column takes max length
            if '\n' in rr_pretty:
                max_rolls_strlen = RESULT_ROLLS_LENGTH_BOUNDS.max
            else:
                # Add 2 for 1 space padding on both sides
                max_rolls_strlen = max(max_rolls_strlen, len(rr_pretty) + 2)
            rr_sum = str(sum(rr.rolls))
            table_body.append([rr.dice, rr_pretty, rr_sum])
            # Add 2 for 1 space padding on both sides
            max_dice_strlen = max(max_dice_strlen, len(rr.dice) + 2)
            max_sum_strlen = max(max_sum_strlen, len(rr_sum) + 2)

        # TODO input validation on roll requests which don't fit on
        #  mobile, maybe this could be a config option?
        if max_dice_strlen > RESULT_DICE_LENGTH_BOUNDS.max:
            print(
                'Warning: dice string exceeds the set '
                'limit for optimal mobile display',
            )
        if max_rolls_strlen > RESULT_ROLLS_LENGTH_BOUNDS.max:
            print(
                'Warning: rolls string exceeds the set '
                'limit for optimal mobile display',
            )
        if max_sum_strlen > RESULT_SUM_LENGTH_BOUNDS.max:
            print(
                'Warning: sum string exceeds the set '
                'limit for optimal mobile display',
            )

        # TODO find a way to have equal character spacing without this
        #  being in a codeblock
        results = codeblock(
            table2ascii(
                header=['dice', 'rolls', 'sum'],
                body=table_body,
                column_widths=[
                    max_dice_strlen,
                    max_rolls_strlen,
                    max_sum_strlen,
                ],
                style=table_style,
            ),
        )
        return results

    @commands.command()
    async def poll(
            self,
            ctx: Context[Bot],
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
            self._cursor.execute(
                'INSERT INTO tasks '
                '(completed, task, message_id, channel_id, end_time)'
                'VALUES (false, "close_poll", ?, ?, ?);',
                (
                    message.id,
                    ctx.channel.id,
                    (datetime.now() + timedelta(seconds=5)).strftime('%m/%d/%y %H:%M:%S'),
                ),
            )
            self._db_conn.commit()
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
            self._cursor.execute(
                'INSERT INTO tasks '
                '(completed, task, message_id, channel_id, end_time)'
                'VALUES (false, "close_poll", ?, ?, ?);',
                (
                    message.id,
                    ctx.channel.id,
                    (datetime.now() + timedelta(seconds=5)).strftime('%m/%d/%y %H:%M:%S'),
                ),
            )
            self._db_conn.commit()
        else:
            await ctx.send(
                'Incorrect syntax, try \"`!poll "<question>"'
                ' "[choice1]" "[choice2]" ...`\"',
            )

    @classmethod
    async def get_results_for_poll(
            cls,
            message: Message,
    ) -> str:
        options: list[str] = [
            # Get content to right of ': '
            m
            # Get option lines (all but the first)
            for m in message.content.split('\n')[1:]
        ]
        option_counts: list[int] = [
            r.count - 1
            for r in message.reactions
        ]
        results: str = '\n'.join([
            f'{opt}: {cnt}' for opt, cnt in zip(options, option_counts)
        ])
        return f'Poll results:\n{results}'

    async def close_poll(
            self,
            message_id: int,
            channel_id: int,
    ) -> None:
        channel = await self._bot.fetch_channel(channel_id)
        if not isinstance(channel, TextChannel):
            return  # TODO handle
        message: Message = await channel.fetch_message(message_id)
        try:
            await message.reply(
                content=await self.get_results_for_poll(message),
            )
        except Forbidden:
            pass  # TODO handle

    @commands.command()
    async def d(
            self,
            ctx: Context[Bot],
            num_sides: int = 6,
    ) -> None:
        """
        Dice rolling command. The commander optionally specifies a
        number of sides to roll on a single dice. If no number is
        specified, a d6 will be rolled. The result will be formatted in
        an ascii table.
        :param ctx: Command context
        :param num_sides: Number of sides on the dice to be rolled
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(num=1, sides=num_sides),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command()
    async def d1(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d1 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(num=1, sides=1),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command(aliases=['flip', 'coinflip'])
    async def d2(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d2 die / coin. The result will be formatted in
        an ascii table.
        :param ctx: Command context
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(num=1, sides=2),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command()
    async def d4(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d4 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(num=1, sides=4),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command()
    async def d6(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d6 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(
                    num=1,
                    sides=6,
                ),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command()
    async def d8(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d8 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(num=1, sides=8),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command()
    async def d10(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d10 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(num=1, sides=10),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command()
    async def d12(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d12 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(num=1, sides=12),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command()
    async def d20(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d20 die. The result will be
        formatted in an ascii table.
        :param ctx: Command context
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(num=1, sides=20),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command()
    async def d100(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Dice rolling command. The commander specified in the command
        itself to roll a d100 die. The result will be formatted in an
        ascii table.
        :param ctx: Command context
        """
        roll_results = Poll.roll_many(
            [
                RollRequest(num=1, sides=100),
            ],
        )
        await ctx.send(Poll.format_roll_results(roll_results))

    @commands.command()
    async def roll(
            self,
            ctx: Context[Bot],
            *args: str
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
        roll_requests = Poll.parse_roll_requests(args)
        roll_results = Poll.roll_many(roll_requests)
        await ctx.send(Poll.format_roll_results(roll_results))


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the poll cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Poll(bot))
