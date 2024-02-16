import shlex
from typing import Literal

from hikari import Snowflakeish


def parse_string(s):
    return shlex.split(s).remove('')


def mention(
        id_: Snowflakeish,
        type_: Literal['channel', 'role', 'user'],
) -> str:
    """Mention an object."""
    match type_:
        case 'channel':
            return f'<#{id_}>'

        case 'user':
            return f'<@{id_}>'

        case 'role':
            return f'<@&{id_}>'
