from __future__ import annotations

import sqlite3
from typing import Literal

import discord
from discord.ext import tasks
from discord.ext.commands import Bot
from discord.ext.commands import Cog
from heckbot.cogs.poll import Poll

db_conn = sqlite3.connect('tasks.db')
cursor = db_conn.cursor()
cursor.execute(
    'CREATE TABLE IF NOT EXISTS tasks'
    '(row_id, completed, task, message_id, channel_id, end_time);',
)
db_conn.commit()

TaskType = Literal['close_poll']


class TaskService:
    def __init__(self, bot):
        self._bot: Bot = bot

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
                poll_cog: Cog | None = self._bot.get_cog('Poll')
                if isinstance(poll_cog, Poll):
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
