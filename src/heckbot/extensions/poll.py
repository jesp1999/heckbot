from __future__ import annotations

import hikari
import lightbulb
from lightbulb import SlashContext
import random
from collections import namedtuple
from datetime import datetime
from datetime import timedelta
from typing import Sequence

from hikari.messages import Message
from heckbot.utils.chatutils import bold
from heckbot.utils.chatutils import codeblock
from table2ascii import PresetStyle
from table2ascii import table2ascii
from table2ascii import TableStyle

from bot import cursor
from bot import db_conn
from bot import HeckBot
from heckbot.utils.utils import parse_string

plugin = lightbulb.Plugin(
    "PollPlugin",
)

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

"""
Cog for enabling polling-related features in the bot.
"""
YES_NO_REACTIONS = ('👍', '👎')
MULTI_CHOICE_REACTIONS = (
    '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣',
    '7️⃣', '8️⃣', '9️⃣', '🔟',
)


def roll_many(
        roll_requests: Sequence[RollRequest],
) -> Sequence[RollResult]:  # nosec B311
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
            rolls.append(random.randint(1, roll_request.sides))  # nosec B311
        roll_results.append(
            RollResult(
                dice=f'{roll_request.num}D{roll_request.sides}',
                rolls=rolls,
            ),
        )
    return roll_results


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
        rr_pretty = get_rolls_pretty(rr.rolls)
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


# TODO find a better way to do this arbitrary number of arguments....
@plugin.command
@lightbulb.option(
    "duration",
    "The duration for the poll (in minutes). Leave empty for 5 minutes.",
    required=False,
    default=5,
)
@lightbulb.option(
    "question",
    "The topic/question for the poll.",
    required=True,
)
@lightbulb.option(
    "choices",
    "Choices for the poll. Specify as a single string"
    " separated by spaces, with quotes delimiting sub-string answers."
    " Leave blank to make a Y/N poll.",
    required=False,
    default='',
)
@lightbulb.command("pollfor", "Creates a poll for a set duration.")
@lightbulb.implements(lightbulb.SlashCommand)
async def poll_for(ctx: SlashContext) -> None:
    """
    Polling command. The commander specifies the poll duration, poll
    question, and answers as space-delimited strings which may
    contain spaces as long as they are within quotes. If the
    commander only specifies the poll question, the answers will be
    assumed to be yes/no.
    :param ctx: Command context
    """
    duration_mins = ctx.options.duration
    question = ctx.options.question
    choices = parse_string(ctx.options.choices)
    await poll_helper(ctx, duration_mins, question, choices, )


@plugin.command
@lightbulb.option(
    "question",
    "The topic/question for the poll.",
    required=True,
)
@lightbulb.option(
    "choices",
    "Choices for the poll. Specify as a single string"
    " separated by spaces, with quotes delimiting sub-string answers."
    " Leave blank to make a Y/N poll.",
    required=False,
    default='',
)
@lightbulb.command("poll", "Creates a poll which closes after 5 minutes.")
@lightbulb.implements(lightbulb.SlashCommand)
async def poll(ctx: SlashContext) -> None:
    """
    Polling command. The commander specifies the poll question and
    answers as space-delimited strings which may contain spaces as
    long as they are within quotes. If the commander only specifies
    the poll question, the answers will be assumed to be yes/no.
    Polls generated with this command time out in 5 minutes.
    :param ctx: Command context
    """
    question = ctx.options.question
    choices = parse_string(ctx.options.choices)
    await poll_helper(ctx, 5, question, choices)


async def poll_helper(
        ctx: SlashContext,
        duration_mins: int,
        question: str,
        choices: Sequence[str],
):
    if len(choices) == 0:
        # Yes/no poll
        question = bold(question)
        message = await ctx.respond(question)
        for reaction in YES_NO_REACTIONS:
            await message.add_reaction(reaction)
        cursor.execute(
            'INSERT INTO tasks '
            '(completed, task, message_id, channel_id, end_time)'
            'VALUES (false, "close_poll", ?, ?, ?);',
            (
                message.id,
                ctx.channel_id,
                (
                        datetime.now() + timedelta(minutes=duration_mins)
                ).strftime('%m/%d/%y %H:%M:%S'),
            ),
        )
        db_conn.commit()
    elif len(choices) > 0:
        # Multi-choice poll
        question = bold(question)
        num_choices = len(choices)
        message_text = question
        for reaction, choice in zip(MULTI_CHOICE_REACTIONS, choices):
            message_text += f'\n{reaction}: {choice}'
        message = await ctx.respond(message_text)
        # TODO handle more poll options than emojis in list
        for reaction in MULTI_CHOICE_REACTIONS[:num_choices]:
            await message.add_reaction(reaction)
        cursor.execute(
            'INSERT INTO tasks '
            '(completed, task, message_id, channel_id, end_time)'
            'VALUES (false, "close_poll", ?, ?, ?);',
            (
                message.id,
                ctx.channel_id,
                (
                    datetime.now() + timedelta(minutes=duration_mins)
                ).strftime('%m/%d/%y %H:%M:%S'),
            ),
        )
        db_conn.commit()
    else:
        await ctx.respond(  # TODO add separate check for poll and pollfor
            'Incorrect syntax, try \"`!poll "<question>"'
            ' "[choice1]" "[choice2]" ...`\"',
        )


async def get_results_for_poll(message: Message) -> str:
    options = message.content.split('\n')[1:]
    if len(options) == 0:
        options = ['👍: Yes', '👎: No']
    option_counts = [r.count - 1 for r in message.reactions]
    results = '\n'.join([
        f'{opt}: {cnt}' for opt, cnt in zip(options, option_counts)
    ])
    return f'Poll results:\n{results}'


async def close_poll(message_id: int, channel_id: int) -> None:
    message: Message = plugin.bot.rest.fetch_message(channel_id, message_id)
    await message.respond(content=await get_results_for_poll(message))


@plugin.command
@lightbulb.option(
    "sides",
    "The number of sides on the die.",
    default=6,
)
@lightbulb.command("d", "Rolls an n-sided die. Leave empty to roll a d6.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander optionally specifies a
    number of sides to roll on a single dice. If no number is
    specified, a d6 will be rolled. The result will be formatted in
    an ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=ctx.options.sides)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.command("d1", "Rolls a 1-sided die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d1(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specified in the command
    itself to roll a d1 die. The result will be formatted in an
    ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=1)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.command("d2", "Rolls a 2-sided die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d2(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specified in the command
    itself to roll a d2 die / coin. The result will be formatted in
    an ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=2)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.command("d4", "Rolls a 4-sided die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d4(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specified in the command
    itself to roll a d4 die. The result will be formatted in an
    ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=4)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.command("d6", "Rolls a 6-sided die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d6(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specified in the command
    itself to roll a d6 die. The result will be formatted in an
    ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=6)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.command("d8", "Rolls an 8-sided die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d8(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specified in the command
    itself to roll a d8 die. The result will be formatted in an
    ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=8)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.command("d10", "Rolls a 10-sided die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d10(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specified in the command
    itself to roll a d10 die. The result will be formatted in an
    ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=10)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.command("d12", "Rolls a 12-sided die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d12(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specified in the command
    itself to roll a d12 die. The result will be formatted in an
    ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=12)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.command("d20", "Rolls a 20-sided die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d20(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specified in the command
    itself to roll a d20 die. The result will be
    formatted in an ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=20)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.command("d1", "Rolls a 1-sided die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def d100(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specified in the command
    itself to roll a d100 die. The result will be formatted in an
    ascii table.
    :param ctx: Command context
    """
    roll_results = roll_many([RollRequest(num=1, sides=100)])
    await ctx.respond(format_roll_results(roll_results))


@plugin.command
@lightbulb.option(
    "rolls",
    "Dice to roll. Specify as a single string"
    " separated by spaces, with quotes delimiting sub-string answers."
    " e.g. 5d6 2d4 1d20 -> 5 d6s, 2 d4s, and 1 d20 will all be rolled.",
    required=False,
    default='',
)
@lightbulb.command("roll", "Rolls a sequence of die.")
@lightbulb.implements(lightbulb.SlashCommand)
async def roll(ctx: SlashContext) -> None:
    """
    Dice rolling command. The commander specifies a series of
    comma-separated dice roll requests, in the following format:
    !roll 5d6 2d4 1d20  -> 5 d6s, 2 d4s, and 1 d20 will all be
    rolled.
    The results will be formatted in an ascii table.
    :param ctx: Command context
    """
    args = parse_string(ctx.options.rolls)
    if any([type(arg) is not str for arg in args]):
        return  # TODO give advice on how to reformat
    roll_requests = parse_roll_requests(args)
    roll_results = roll_many(roll_requests)
    await ctx.respond(format_roll_results(roll_results))
