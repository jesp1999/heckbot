from unittest import mock

import discord.ext.test as dpytest
import pytest
import pytest_asyncio

from bot import HeckBot
from src.cogs.poll import Poll


# noinspection PyProtectedMember
@pytest_asyncio.fixture
async def bot():
    b = HeckBot()
    await b._async_setup_hook()
    await b.add_cog(Poll(b))
    dpytest.configure(b)
    return b


def expected_dice_content(sides: int):
    if sides < 10:
        return f'''```╔══════╤═══════╤═════╗
║ dice │ rolls │ sum ║
╠══════╪═══════╪═════╣
║ 1D{sides}  │   1   │  1  ║
╚══════╧═══════╧═════╝```'''
    elif sides < 100:
        return f'''```╔══════╤═══════╤═════╗
║ dice │ rolls │ sum ║
╠══════╪═══════╪═════╣
║ 1D{sides} │   1   │  1  ║
╚══════╧═══════╧═════╝```'''
    else:
        return f'''```╔═══════╤═══════╤═════╗
║ dice  │ rolls │ sum ║
╠═══════╪═══════╪═════╣
║ 1D{sides} │   1   │  1  ║
╚═══════╧═══════╧═════╝```'''


@pytest.mark.asyncio
@pytest.mark.parametrize("command,expected_text",
                         [('d1', expected_dice_content(1)),
                          ('d2', expected_dice_content(2)),
                          ('flip', expected_dice_content(2)),
                          ('d4', expected_dice_content(4)),
                          ('d6', expected_dice_content(6)),
                          ('d', expected_dice_content(6)),
                          ('d8', expected_dice_content(8)),
                          ('d10', expected_dice_content(10)),
                          ('d12', expected_dice_content(12)),
                          ('d20', expected_dice_content(20)),
                          ('d100', expected_dice_content(100))],
                         ids=['d1', 'd2', 'flip', 'd4', 'd6', 'd', 'd8', 'd10',
                              'd12', 'd20', 'd100'])
@mock.patch('random.randint')
async def test_single_dice(mock_randint, command, expected_text, bot):
    mock_randint.return_value = 1
    await dpytest.message(f'!{command}')
    assert dpytest.verify().message().content(expected_text)
