from __future__ import annotations

from typing import Final

import discord
from discord import RawReactionActionEvent
from discord import Role
from discord.ext import commands
from discord.ext.commands import Context
from heckbot.adapter.sqlite_adaptor import SqliteAdaptor

from bot import HeckBot

MAX_REACTIONS_PER_MESSAGE: Final[int] = 20


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
        self._db = SqliteAdaptor()
        self._db.run_query('''PRAGMA foreign_keys = 1''')
        self._db.run_query('''\
            CREATE TABLE IF NOT EXISTS role_categories
            (guild_id TEXT NOT NULL,
            role_category TEXT NOT NULL,
            PRIMARY KEY (guild_id, role_category));
        ''')
        self._db.run_query('''\
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
        self._db.run_query('''\
            CREATE TABLE IF NOT EXISTS role_messages
            (guild_id TEXT NOT NULL,
            channel_id INT NOT NULL,
            message_id INT NOT NULL,
            role_category TEXT NOT NULL DEFAULT 'Miscellaneous',
            message_index INT NOT NULL DEFAULT 1,

            PRIMARY KEY (guild_id, channel_id, message_id, message_index),
            FOREIGN KEY (role_category) REFERENCES role_categories (role_category));
        ''')
        self._db.commit_and_close()

    @commands.command(aliases=['createrole', 'addrole', 'rolerequest'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def create_role(
            self, ctx: Context, name: str, description: str,
            category: str, emoji: str,
    ):
        if not any(r.name == name for r in ctx.guild.roles):
            await ctx.guild.create_role(name=name)
        guild_id = str(ctx.guild.id)
        results = self._db.run_query(
            '''SELECT channel_id, message_id, role_category FROM role_messages
            WHERE guild_id=?;''', (guild_id,),
        )
        if len(results) < 1:
            return
        category_exists = any(r['role_category'] == category for r in results)
        roles_params_list = []
        message_params_list = []
        for row in results:
            if row['role_category'] != category:
                continue
            channel_id = row['channel_id']
            message_id = row['message_id']
            channel = await ctx.guild.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
            if message.content.count('\n') >= MAX_REACTIONS_PER_MESSAGE:
                message = await channel.send(
                    f'**{category}**\n'
                    '--------------------------\n'
                    f'{emoji} for {description}',
                )
                await message.add_reaction(emoji)
                message_params_list.append(
                    (guild_id, str(channel.id), str(message.id), row['message_index'] + 1))
            else:
                content = message.content + f'\n{emoji} for {description}'
                await message.edit(content=content)
                await message.add_reaction(emoji)
            roles_params_list.append((guild_id, name, description, category, emoji))
        if not category_exists:
            channels = {r['channel_id'] for r in results}
            for channel in channels:
                channel = await ctx.guild.fetch_channel(channel)
                message = await channel.send(
                    f'**{category}**\n'
                    '--------------------------\n'
                    f'{emoji} for {description}',
                )
                await message.add_reaction(emoji)
                message_params_list.append((guild_id, str(channel.id), str(message.id), 1))
        if message_params_list:
            self._db.run_query_many(
                '''INSERT INTO role_messages (guild_id, channel_id, message_id, message_index)
                VALUES (?, ?, ?, ?);''', message_params_list,
            )
        if roles_params_list:
            self._db.run_query_many(
                '''INSERT INTO roles
                    (guild_id, role_name, role_description,
                    role_category, role_react)
                    VALUES (?, ?, ?, ?, ?);''', roles_params_list,
            )
        self._db.commit_and_close()

    @commands.command(aliases=['deleterole', 'delrole', 'removerole', 'rmrole'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def delete_role(
            self, ctx: Context, name: str,
    ):
        guild_id = str(ctx.guild.id)
        role_rows = self._db.run_query(
            '''SELECT role_react, role_description, role_category, role_react FROM roles
            WHERE guild_id=? AND role_name=?;''', (guild_id, name),
        )
        if len(role_rows) < 1:
            return
        role_row = role_rows[0]
        react = role_row['role_react']
        desc = role_row['role_description']
        category = role_row['role_category']
        message_rows = self._db.run_query(
            '''SELECT channel_id, message_id FROM role_messages
            WHERE guild_id=? AND role_category=?;''', (guild_id, category),
        )
        role_string = f'{react} for {desc}'
        # Doesn't delete the role from the guild, just removes it from role
        # request messages
        for row in message_rows:
            channel_id = row['channel_id']
            message_id = row['message_id']
            channel = await ctx.guild.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
            content = message.content.replace(
                role_string, '',
            ).replace('\n\n', '\n')
            await message.edit(content=content)
            await message.clear_reaction(react)
        self._db.run_query(
            '''DELETE FROM roles WHERE guild_id=? AND role_name=?;''',
            (guild_id, name),
        )
        self._db.commit_and_close()

    @commands.command(aliases=['createrolesmessage', 'createrolesmsg'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def create_roles_message(self, ctx: Context):
        """
        Sends a role-reaction-enabled message in the current chat.
        :param ctx: Context of the command
        """
        result = self._db.run_query(
            '''SELECT role_name, role_description, role_category, role_react
            FROM roles WHERE guild_id=?
            AND role_opt_in=TRUE;
            ''',
            (ctx.guild.id,),
        )
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

        params = []
        for category in role_map:
            message_index = 1
            message = await ctx.channel.send(
                f'**{category}**\n'
                '--------------------------\n' +
                '\n'.join([
                    f'{react_map[role]} for {role_map[category][role]}'
                    for role in role_map[category]
                ]),
            )
            for role in role_map[category]:
                await message.add_reaction(react_map[role])
            params.append((
                str(ctx.guild.id),
                str(ctx.channel.id),
                str(message.id),
                category,
                message_index
            ))
        self._db.run_query_many(
            '''INSERT INTO role_messages (guild_id, channel_id, message_id, role_category, message_index)
            VALUES (?, ?, ?);''',
            params,
        )
        self._db.commit_and_close()
        await ctx.message.delete()

    async def _fetch_roles_for_reaction_change(
            self, payload: RawReactionActionEvent,
    ) -> list[Role]:
        message_id = str(payload.message_id)
        channel_id = str(payload.channel_id)
        guild_id = str(payload.guild_id)
        guild = await self._bot.fetch_guild(payload.guild_id)
        role_react_message = self._db.run_query(
            '''SELECT COUNT(*) AS num_messages FROM role_messages
            WHERE guild_id=?
            AND channel_id=?
            AND message_id=?;''',
            (guild_id, channel_id, message_id),
        )[0]['num_messages'] > 0
        if role_react_message:
            role_names = [
                r['role_name'] for r in self._db.run_query(
                    '''SELECT role_name FROM roles
                WHERE guild_id=?
                AND role_react=?;''',
                    (guild_id, str(payload.emoji)),
                )
            ]
            roles = [
                discord.utils.get(guild.roles, name=role_name)
                for role_name in role_names
            ]
            self._db.commit_and_close()
            return roles
        return []

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        # channel = await self._bot.fetch_channel(payload.channel_id)
        # message = await channel.fetch_message(payload.message_id)
        # reactions = message.reactions
        # if not any(r.emoji == payload.emoji for r in reactions):
        #     member = await self._bot.get_guild(payload.guild_id).fetch_member(payload.user_id)
        #     await message.remove_reaction(payload.emoji, member)
        #     return
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
