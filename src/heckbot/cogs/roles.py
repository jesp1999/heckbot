from __future__ import annotations

import asyncio
import sqlite3
from sqlite3 import Row

import discord
from discord import client, PartialEmoji
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from heckbot.adapter.reaction_table_adapter import ReactionTableAdapter

from bot import HeckBot


class Roles(commands.Cog):
    """
    Cog for enabling role-selection related features in the bot.
    """

    def __init__(
            self,
            bot: HeckBot,
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot = bot

        db_conn = sqlite3.connect('roles.db')
        db_conn.row_factory = Row
        self._cursor = db_conn.cursor()
        self._cursor.execute("PRAGMA foreign_keys = 1")
        self._cursor.execute(
            'CREATE TABLE IF NOT EXISTS role_categories'
            '(role_category TEXT UNIQUE NOT NULL);',
        )
        self._cursor.execute(
            'CREATE TABLE IF NOT EXISTS roles'
            '(role_name TEXT UNIQUE NOT NULL,'
            'role_description TEXT NOT NULL,'
            'role_category TEXT NOT NULL,'
            'role_react TEXT NOT NULL,'
            'FOREIGN KEY (role_category) REFERENCES role_categories (role_category));',
        )
        db_conn.commit()

    @commands.command(aliases=['createrolesmessage', 'createrolesmsg'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def create_roles_message(self, ctx: Context):
        """
        Sends a role-reaction-enabled message in the current chat.
        :param ctx: Context of the command
        """
        result = self._cursor.execute('SELECT * FROM roles;').fetchall()
        role_map = {}
        react_map = {}
        for item in result:
            if item[2] not in role_map:
                role_map[item[2]] = []
            role_map[item[2]].append(item[1])
            emoji = PartialEmoji.from_str(item[3])
            react_map[item[1]] = emoji
        role_msg = '\n\n'.join([
            (
                    f'**{category}**\n'
                    '--------------------------\n' +
                    '\n'.join([
                        f'{react_map[role]} for {role}' for role in role_map[category]
                    ])
            ) for category in role_map
        ])
        message = await ctx.author.send(role_msg)

        # TODO fix this
        for react in react_map.values():
            await message.add_reaction(react)


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the react-match cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Roles(bot))
