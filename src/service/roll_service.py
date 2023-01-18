import random
from collections import namedtuple
from math import ceil, floor

from table2ascii import table2ascii, PresetStyle

RESULT_DICE_LENGTH = 9
RESULT_ROLLS_LENGTH = 30
RESULT_SUM_LENGTH = RESULT_DICE_LENGTH - 1
RESULT_TOTAL_LENGTH = RESULT_DICE_LENGTH + RESULT_ROLLS_LENGTH + RESULT_SUM_LENGTH + 10

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
    def format_roll_results(roll_results: list[RollResult]) -> str:
        results = '```' + table2ascii(
            header=['dice', 'rolls', 'sum'],
            body=[
                [rr.dice, ' '.join([str(r) for r in rr.rolls]), sum(rr.rolls)]
                for rr in roll_results
            ],
            style=PresetStyle.double_thin_box
        ) + '```'
        return results
