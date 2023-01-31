import sqlite3

import discord
from discord.ext import tasks
from discord.ext.commands import Bot, Cog

from src.cogs.poll import Poll

db_conn = sqlite3.connect('tasks.db')
cursor = db_conn.cursor()
cursor.execute(
    'CREATE TABLE IF NOT EXISTS tasks'
    '(row_id, completed, message_id, channel_id, end_time);'
)
db_conn.commit()


class TaskService:
    def __init__(self, bot):
        self._bot: Bot = bot

    @tasks.loop()
    async def poll_results_task(self):
        cursor.execute(
            'SELECT * FROM tasks WHERE NOT completed ORDER BY end_time LIMIT 1;'
        )
        next_task = await cursor.fetchone()

        # if no remaining tasks, stop the loop
        if next_task is None:
            self.poll_results_task.cancel()

        # sleep until the task should be done
        await discord.utils.sleep_until(next_task['end_time'])

        # perform task
        poll_cog: Cog = self._bot.get_cog('Poll')
        poll_cog: Poll
        await poll_cog.close_poll(
            next_task['message_id'],
            next_task['channel_id']
        )

        cursor.execute('UPDATE tasks SET completed = true WHERE row_id = $1',
                       next_task['row_id'])
        db_conn.commit()

        self.poll_results_task.before_loop(discord.Client.wait_until_ready)
        self.poll_results_task.start()

        # in a command that adds new task in db
        if self.poll_results_task.is_running():
            self.poll_results_task.restart()
        else:
            self.poll_results_task.start()
