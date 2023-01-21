import random
from collections import namedtuple

from table2ascii import table2ascii, PresetStyle, TableStyle

Bounds: namedtuple = namedtuple('Bounds', ['min', 'max'])
RESULT_DICE_LENGTH_BOUNDS: Bounds = Bounds(6, 9)
RESULT_ROLLS_LENGTH_BOUNDS: Bounds = Bounds(7, 21)
RESULT_SUM_LENGTH_BOUNDS: Bounds = Bounds(5, 8)

RollRequest: namedtuple = namedtuple('RollRequest', ['num', 'sides'])
RollResult: namedtuple = namedtuple('RollResult', ['dice', 'rolls'])


class RollService:
    """
    Service class which encapsulates all logic behind dice rolling
    commands from the poll cog.
    """

    @staticmethod
    def roll_many(
            roll_requests: list[RollRequest]
    ) -> list[RollResult]:
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
                    rolls=rolls
                )
            )
        return roll_results

    @staticmethod
    def parse_roll_requests(
            roll_requests: list[str]
    ) -> list[RollRequest]:
        """
        Parses raw roll requests from command args into the RoleRequest
        data type.
        :param roll_requests: Raw roll requests from command args
        :return: Roll requests as RoleRequest data types
        """
        parsed_roll_requests = []
        for roll_request in roll_requests:
            roll_request_parts = roll_request.lower().split('d')
            if len(roll_request_parts) == 2:
                num = int(roll_request_parts[0])
                sides = int(roll_request_parts[1])
                parsed_roll_requests.append(
                    RollRequest(
                        num=num, sides=sides
                    )
                )
        return parsed_roll_requests

    @staticmethod
    def get_rolls_pretty(
            rolls: list[int],
            line_length: int = RESULT_ROLLS_LENGTH_BOUNDS.max
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
            roll_results: list[RollResult],
            table_style: TableStyle = PresetStyle.double_thin_box
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
            rr_pretty = RollService.get_rolls_pretty(rr.rolls)
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
            print('Warning: dice string exceeds the set '
                  'limit for optimal mobile display')
        if max_rolls_strlen > RESULT_ROLLS_LENGTH_BOUNDS.max:
            print('Warning: rolls string exceeds the set '
                  'limit for optimal mobile display')
        if max_sum_strlen > RESULT_SUM_LENGTH_BOUNDS.max:
            print('Warning: sum string exceeds the set '
                  'limit for optimal mobile display')

        # TODO find a way to have equal character spacing without this
        #  being in a codeblock
        results = '```' + table2ascii(
            header=['dice', 'rolls', 'sum'],
            body=table_body,
            column_widths=[
                max_dice_strlen,
                max_rolls_strlen,
                max_sum_strlen
            ],
            style=table_style
        ) + '```'
        return results
