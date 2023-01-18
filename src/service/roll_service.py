import random
from collections import namedtuple
from math import ceil, floor

RESULT_DICE_LENGTH = 9
RESULT_ROLLS_LENGTH = 30
RESULT_SUM_LENGTH = RESULT_DICE_LENGTH - 1
RESULT_TOTAL_LENGTH = RESULT_DICE_LENGTH + RESULT_ROLLS_LENGTH + RESULT_SUM_LENGTH + 4

RollRequest = namedtuple('RollRequest', ['num', 'sides'])
RollResult = namedtuple('RollResult', ['dice', 'rolls'])


class RollService:
    @staticmethod
    def roll_many(roll_requests: list[RollRequest]) -> list[RollResult]:
        roll_results = []
        for roll_request in roll_requests:
            rolls = []
            for roll in range(roll_request.num):
                rolls.append(random.randint(1, roll_request.sides))
            roll_results.append(RollResult(dice=f'{roll_request.num}D{roll_request.sides}', rolls=rolls))
        return roll_results

    @staticmethod
    def parse_roll_requests(roll_requests: list[str]) -> list[RollRequest]:
        parsed_roll_requests = []
        for roll_request in roll_requests:
            roll_request_parts = roll_request.lower().split('d')
            if len(roll_request_parts) == 2:
                num = int(roll_request_parts[0])
                sides = int(roll_request_parts[1])
                parsed_roll_requests.append(RollRequest(num=num, sides=sides))
        return parsed_roll_requests

    @staticmethod
    def pad_with_spaces_to_length(text: str, length: int):
        num_spaces = length - len(text)
        return (' ' * floor(num_spaces / 2)) + text + (' ' * ceil(num_spaces / 2))

    @staticmethod
    def format_roll_line(p1, p2, p3):
        return 'X{}X{}X{}X'.format(
            RollService.pad_with_spaces_to_length(p1, RESULT_DICE_LENGTH),
            RollService.pad_with_spaces_to_length(p2, RESULT_ROLLS_LENGTH),
            RollService.pad_with_spaces_to_length(p3, RESULT_SUM_LENGTH)
        )

    @staticmethod
    def format_roll_results(roll_results: list[RollResult]) -> str:
        roll_result_boundary = 'X' * RESULT_TOTAL_LENGTH
        formatted_roll_results: list[str] = [
            '```',
            roll_result_boundary,
            RollService.format_roll_line('dice', 'rolls', 'sum'),
            roll_result_boundary
        ]
        for i, rr in enumerate(roll_results):
            roll_lines = []
            roll_line = str(rr.rolls[0])
            for r in rr.rolls[1:]:
                if len(roll_line) + 3 + len(str(r)) > RESULT_ROLLS_LENGTH:
                    roll_lines.append(roll_line)
                    roll_line = str(r)
                else:
                    roll_line += ' ' + str(r)
            roll_lines.append(roll_line)
            sum_part = str(sum(rr.rolls))
            formatted_roll_results.append(RollService.format_roll_line(rr.dice, roll_lines[0], sum_part))
            for j in range(1, len(roll_lines)):
                formatted_roll_results.append(RollService.format_roll_line('', roll_lines[j], ''))
            if i != len(roll_results) - 1:
                formatted_roll_results.append(RollService.format_roll_line('', '', ''))

        formatted_roll_results.append(roll_result_boundary)
        formatted_roll_results.append('```')
        return '\n'.join(formatted_roll_results)
