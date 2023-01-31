import asyncio
import os
import sys
from datetime import datetime
from os.path import join, dirname
from typing import Final

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.service.config_service import ConfigService
from src.service.task_service import TaskService
from src.types.constants import (PRIMARY_GUILD_ID,
                                 ADMIN_CONSOLE_CHANNEL_ID,
                                 BOT_CUSTOM_STATUS,
                                 BOT_COMMAND_PREFIX)

load_dotenv(join(dirname(__file__), '.env'))

token: str = os.getenv('DISCORD_TOKEN')

cogs: Final[list] = [
    'config',
    'events',
    'gif',
    'moderation',
    'poll',
    'react'
]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.typing = True
intents.presences = True
intents.members = True


class HeckBot(commands.Bot):
    after_ready_task: asyncio.Task[None]

    def __init__(self):
        super().__init__(
            command_prefix=BOT_COMMAND_PREFIX,
            intents=intents,
            owner_id=277859399903608834,
            reconnect=True,
            case_insensitive=False
        )
        self.uptime: datetime = datetime.utcnow()
        self._task_service = None

    async def setup_hook(
            self
    ) -> None:
        """
        Asynchronous setup code for the bot before gateway connection
        :return:
        """
        self.after_ready_task = asyncio.create_task(self.after_ready())

        self.remove_command('help')

        # load cogs
        for cog in cogs:
            try:
                await self.load_extension(f'src.cogs.{cog}')
            except Exception as ex:
                print(f'Could not load extension {cog}: {ex}')
                raise ex

    async def after_ready(
            self
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
            activity=discord.Game(BOT_CUSTOM_STATUS)
        )

        self._task_service = TaskService(self)

        # alert channels of bot online status
        for guild in self.guilds:
            ConfigService.generate_default_config(self, str(guild.id))
            print(f'{self.user} has connected to the following guild: '
                  f'{guild.name}(id: {guild.id})')
            if guild.id == PRIMARY_GUILD_ID:
                channel = guild.get_channel(ADMIN_CONSOLE_CHANNEL_ID)
                await channel.send(
                    ConfigService.get_config_option(
                        str(guild.id),
                        'messages',
                        'welcomeMessage'
                    )
                )

        print(
            f"----------------HeckBot---------------------"
            f"\nBot is online as user {self.user}"
            f"\nConnected to {(len(self.guilds))} guilds."
            f"\nDetected OS: {sys.platform.title()}"
            f"\n--------------------------------------------"
        )


HeckBot().run(token)
