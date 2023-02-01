import asyncio
import os
import random
import sys
from datetime import datetime
from os.path import join, dirname
from typing import Final

import discord
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

from heckbot.service.config_service import ConfigService
from heckbot.service.task_service import TaskService
from heckbot.types.constants import (PRIMARY_GUILD_ID,
                                     ADMIN_CONSOLE_CHANNEL_ID,
                                     BOT_CUSTOM_STATUS,
                                     BOT_COMMAND_PREFIX)

load_dotenv(join(dirname(__file__), '.env'))


class HeckBot(commands.Bot):
    _token: str = os.getenv('DISCORD_TOKEN')
    after_ready_task: asyncio.Task[None]
    _cogs: Final[list] = [
        'config',
        'events',
        'gif',
        'moderation',
        'poll',
        'react'
    ]

    def __init__(self):
        intents: Intents = Intents(
            messages=True,
            message_content=True,
            typing=True,
            presences=True,
            members=True)
        super().__init__(
            command_prefix=BOT_COMMAND_PREFIX,
            intents=intents,
            owner_id=277859399903608834,
            reconnect=True,
            case_insensitive=False
        )
        self.uptime: datetime = datetime.utcnow()
        self._task_service = None

    def run(self, **kwargs):
        load_dotenv(join(dirname(__file__), '.env'))
        super().run(os.getenv('DISCORD_TOKEN'))

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
        for cog in self._cogs:
            try:
                await self.load_extension(f'src.heckbot.cogs.{cog}')
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


if __name__ == '__main__':
    random.seed(0)
    HeckBot().run()
