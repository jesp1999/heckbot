from __future__ import annotations

import asyncio
import sqlite3
from sqlite3 import Row

import discord
from discord import client
from discord import Emoji
from discord import Member
from discord import Message
from discord import PartialEmoji
from discord import RawReactionActionEvent
from discord import Reaction
from discord import User
from discord.abc import Snowflake
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
        self._connection = None
        self.cursor.execute('''PRAGMA foreign_keys = 1''')
        self.cursor.execute('''\
            CREATE TABLE IF NOT EXISTS role_categories
            (guild_id TEXT NOT NULL,
            role_category TEXT NOT NULL,
            PRIMARY KEY (guild_id, role_category));
        ''')
        self.cursor.execute('''\
            CREATE TABLE IF NOT EXISTS roles
            (guild_id TEXT NOT NULL,
            role_name TEXT NOT NULL,
            role_description TEXT NOT NULL,
            role_category TEXT NOT NULL DEFAULT 'Miscellaneous',
            role_react TEXT NOT NULL,
            role_opt_in BOOLEAN NOT NULL DEFAULT TRUE,
            PRIMARY KEY (guild_id, role_name),
            FOREIGN KEY (role_category) REFERENCES role_categories (role_category));
        ''')
        self.cursor.execute('''\
            CREATE TABLE IF NOT EXISTS role_messages
            (guild_id TEXT NOT NULL,
            channel_id INT NOT NULL,
            message_id INT NOT NULL,
            PRIMARY KEY (guild_id, channel_id, message_id));
        ''')
        self.commit_and_close()

    @property
    def cursor(self):
        if self._connection is None:
            self._connection = sqlite3.connect('roles.db')
            self._connection.row_factory = sqlite3.Row
        return self._connection.cursor()

    def commit_and_close(self):
        if self._connection:
            self._connection.commit()
            self._connection.close()
            self._connection = None

    @commands.command(aliases=['createrolesmessage', 'createrolesmsg'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def create_roles_message(self, ctx: Context):
        """
        Sends a role-reaction-enabled message in the current chat.
        :param ctx: Context of the command
        """
        result = self.cursor.execute(
            '''\
            SELECT role_name, role_description, role_category, role_react
            FROM roles WHERE guild_id=:guild_id
            AND role_opt_in=TRUE;''',
            {'guild_id': str(ctx.guild.id)},
        ).fetchall()
        role_map = {}
        react_map = {}
        for item in result:
            name = item['role_name']
            desc = item['role_description']
            category = item['role_category']
            react = item['role_react']
            if category not in role_map:
                role_map[category] = {}
            role_map[category][name] = desc
            react_map[name] = react

        for category in role_map:
            message = await ctx.channel.send(
                f'**{category}**\n'
                '--------------------------\n' +
                '\n'.join([
                    f'{react_map[role]} for {role}'
                    for role in role_map[category]
                ]),
            )
            for role in role_map[category]:
                await message.add_reaction(react_map[role])

            self.cursor.execute(
                '''
                INSERT INTO role_messages (guild_id, channel_id, message_id)
                VALUES (:guild_id, :channel_id, :message_id);''',
                {
                    'guild_id': str(ctx.guild.id),
                    'channel_id': str(ctx.channel.id),
                    'message_id': str(message.id),
                },
            )
            self.commit_and_close()

    async def _fetch_roles_for_reaction_change(
            self, payload: RawReactionActionEvent,
    ) -> list[int]:
        message_id = str(payload.message_id)
        channel_id = str(payload.channel_id)
        guild_id = str(payload.guild_id)
        guild = await self._bot.fetch_guild(payload.guild_id)
        role_react_message = self.cursor.execute(
            '''\
            SELECT COUNT(*) AS num_messages FROM role_messages
            WHERE guild_id=:guild_id
            AND channel_id=:channel_id
            AND message_id=:message_id;''',
            {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'message_id': message_id,
            },
        ).fetchone()['num_messages'] > 0
        if role_react_message:
            role_names = [
                r['role_name'] for r in self.cursor.execute(
                    '''\
                SELECT role_name FROM roles
                WHERE guild_id=:guild_id
                AND role_react=:role_react;''',
                    {
                        'guild_id': guild_id,
                        'role_react': str(payload.emoji),
                    },
                ).fetchall()
            ]
            roles = [
                discord.utils.get(guild.roles, name=role_name)
                for role_name in role_names
            ]
            self.commit_and_close()
            return roles
        return []

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        roles = await self._fetch_roles_for_reaction_change(payload)
        await payload.member.add_roles(*roles)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        roles = await self._fetch_roles_for_reaction_change(payload)
        guild = await self._bot.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        await member.remove_roles(*roles)


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the react-match cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Roles(bot))
