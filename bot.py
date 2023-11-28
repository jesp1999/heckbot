from __future__ import annotations

from pathlib import Path
from sqlite3 import Row
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from heckbot.cogs.poll import Poll

import asyncio
import os
import random
import sqlite3
import sys
from datetime import datetime
from typing import Final
from typing import Literal
from typing import cast

import discord
from discord import Intents
from discord import TextChannel
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
from heckbot.adapter.config_adapter import ConfigAdapter
from heckbot.types.constants import ADMIN_CONSOLE_CHANNEL_ID
from heckbot.types.constants import BOT_COMMAND_PREFIX
from heckbot.types.constants import BOT_CUSTOM_STATUS
from heckbot.types.constants import PRIMARY_GUILD_ID

TASK_LOOP_PERIOD = 5  # seconds

load_dotenv(Path(__file__).parent / '.env')

db_conn = sqlite3.connect('tasks.db')
db_conn.row_factory = Row
cursor = db_conn.cursor()
cursor.execute('DROP TABLE IF EXISTS tasks;')
cursor.execute(
    'CREATE TABLE IF NOT EXISTS tasks'
    '(completed BOOLEAN, task TEXT, message_id INT, channel_id INT, end_time TEXT);',
)
db_conn.commit()

TaskType = Literal['close_poll']


class HeckBot(commands.Bot):
    after_ready_task: asyncio.Task[None]
    _cogs: Final = [
        'config',
        'events',
        'message',
        'moderation',
        'poll',
        'react',
        'roles',
    ]

    def __init__(self):
        intents = Intents(
            auto_moderation=True,
            guilds=True,
            members=True,
            messages=True,
            message_content=True,
            moderation=True,
            presences=True,
            reactions=True,
            typing=True,
            voice_states=True,
        )
        super().__init__(
            command_prefix=BOT_COMMAND_PREFIX,
            intents=intents,
            owner_id=277859399903608834,
            reconnect=True,
            case_insensitive=False,
        )
        self.uptime = datetime.utcnow()
        self.config = ConfigAdapter()

    @tasks.loop(seconds=TASK_LOOP_PERIOD)
    async def task_loop(self):
        cursor.execute(
            'SELECT rowid,* FROM tasks WHERE NOT completed ORDER BY end_time LIMIT 1;',
        )
        next_task = cursor.fetchone()
        # if no remaining tasks, stop the loop
        if next_task is None:
            return

        # sleep until the task should be done
        await discord.utils.sleep_until(
            datetime.strptime(next_task['end_time'], '%m/%d/%y %H:%M:%S'),
        )
        # perform task
        task_type = next_task['task']
        match task_type:
            case 'close_poll':
                poll_cog = cast('Poll', self.get_cog('Poll'))
                await poll_cog.close_poll(
                    next_task['message_id'],
                    next_task['channel_id'],
                )
            case _:  # default
                raise NotImplementedError

        cursor.execute(
            'UPDATE tasks SET completed = true WHERE rowid = ?;',
            (next_task['rowid'],),
        )
        db_conn.commit()

    def run(self, **kwargs):
        load_dotenv(Path(__file__).parent / '.env')
        super().run(os.environ['DISCORD_TOKEN'])

    async def setup_hook(
            self,
    ) -> None:
        """
        Asynchronous setup code for the bot before gateway connection
        :return:
        """
        self.after_ready_task = asyncio.create_task(self.after_ready())
        self.task_loop.start()

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
