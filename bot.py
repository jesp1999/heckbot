from __future__ import annotations

import asyncio
import os
import random
import sqlite3
import sys
from datetime import datetime
from os.path import dirname
from os.path import join
from typing import Final
from typing import Literal

import discord
from discord import Intents
from discord import TextChannel
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
from heckbot.adaptor.config_adaptor import ConfigAdaptor
from heckbot.types.constants import ADMIN_CONSOLE_CHANNEL_ID
from heckbot.types.constants import BOT_COMMAND_PREFIX
from heckbot.types.constants import BOT_CUSTOM_STATUS
from heckbot.types.constants import PRIMARY_GUILD_ID

load_dotenv(join(dirname(__file__), '.env'))

db_conn = sqlite3.connect('tasks.db')
cursor = db_conn.cursor()
cursor.execute('DROP TABLE IF EXISTS tasks;')
cursor.execute(
    'CREATE TABLE IF NOT EXISTS tasks'
    '(row_id INT, completed BOOLEAN, task TEXT, message_id INT, channel_id INT, end_time TEXT);',
)
db_conn.commit()

TaskType = Literal['close_poll']


class HeckBot(commands.Bot):
    after_ready_task: asyncio.Task[None]
    _cogs: Final[list[str]] = [
        'config',
        'events',
        'gif',
        'moderation',
        'poll',
        'react',
    ]

    def __init__(self):
        intents: Intents = Intents(
            messages=True,
            message_content=True,
            typing=True,
            presences=True,
            members=True,
        )
        super().__init__(
            command_prefix=BOT_COMMAND_PREFIX,
            intents=intents,
            owner_id=277859399903608834,
            reconnect=True,
            case_insensitive=False,
        )
        self.uptime: datetime = datetime.utcnow()
        self.config = ConfigAdaptor()

    @tasks.loop()
    async def task_loop(self):
        cursor.execute(
            'SELECT * FROM tasks WHERE NOT completed ORDER BY end_time LIMIT 1;',
        )
        next_task = await cursor.fetchone()

        # if no remaining tasks, stop the loop
        if next_task is None:
            self.task_loop.cancel()

        # sleep until the task should be done
        await discord.utils.sleep_until(next_task['end_time'])

        # perform task
        task_type = next_task['task_type']
        match task_type:
            case 'close_poll':
                poll_cog = self.get_cog('Poll')
                await poll_cog.close_poll(
                    next_task['message_id'],
                    next_task['channel_id'],
                )
            case _:  # default
                raise NotImplementedError

        cursor.execute(
            'UPDATE tasks SET completed = true WHERE row_id = $1',
            next_task['row_id'],
        )
        db_conn.commit()

        self.task_loop.before_loop(discord.Client.wait_until_ready)
        self.task_loop.start()

        # in a command that adds new task in db
        if self.task_loop.is_running():
            self.task_loop.restart()
        else:
            self.task_loop.start()

    def run(self, **kwargs):
        load_dotenv(join(dirname(__file__), '.env'))
        super().run(os.environ['DISCORD_TOKEN'])

    async def setup_hook(
            self,
    ) -> None:
        """
        Asynchronous setup code for the bot before gateway connection
        :return:
        """
        self.after_ready_task = asyncio.create_task(self.after_ready())

        self.remove_command('help')

        # load cogs
        for cog in self._cogs:
            try:
                await self.load_extension(f'src.heckbot.cogs.{cog}')
            except Exception as ex:
                print(f'Could not load extension {cog}: {ex}')
                raise ex

    async def after_ready(
            self,
    ):
        """
        Asynchronous post-ready code for the bot
        :return:
        """
        await self.wait_until_ready()

        self.uptime = datetime.utcnow()

        await self.change_presence(
            status=discord.Status.online,
            # TODO save this constant into a global config elsewhere
            activity=discord.Game(BOT_CUSTOM_STATUS),
        )

        # alert channels of bot online status
        for guild in self.guilds:
            print(
                f'{self.user} has connected to the following guild: '
                f'{guild.name}(id: {guild.id})',
            )
            if guild.id == PRIMARY_GUILD_ID:
                channel = guild.get_channel(ADMIN_CONSOLE_CHANNEL_ID)
                if isinstance(channel, TextChannel):
                    await channel.send(
                        self.config.get_message(guild.id, 'welcomeMessage'),
                    )

        print(
            f'----------------HeckBot---------------------'
            f'\nBot is online as user {self.user}'
            f'\nConnected to {(len(self.guilds))} guilds.'
            f'\nDetected OS: {sys.platform.title()}'
            f'\n--------------------------------------------',
        )


if __name__ == '__main__':
    random.seed(0)
    HeckBot().run()
