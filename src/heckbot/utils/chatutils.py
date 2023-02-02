from __future__ import annotations


def bold(
        text: str,
) -> str:
    return '**' + text + '**'


def italicize(
        text: str,
) -> str:
    return '*' + text + '*'


def code(
        text: str,
) -> str:
    return '`' + text + '`'


def codeblock(
        text: str,
) -> str:
    return '```' + text + '```'
