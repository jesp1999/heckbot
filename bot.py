import os
import sys
from os.path import join, dirname
from typing import NoReturn

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.cogs import react, poll, gif, config
from src.types.constants import (WELCOME_CHANNEL_ID, PRIMARY_GUILD_ID,
                                 WELCOME_MESSAGE, ADMIN_CONSOLE_CHANNEL_ID,
                                 BOT_ONLINE_MESSAGE, BOT_CUSTOM_STATUS,
                                 BOT_COMMAND_PREFIX)


def main() -> NoReturn:
    load_dotenv(join(dirname(__file__), '.env'))

    token: str = os.getenv('DISCORD_TOKEN')

    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    intents.typing = True
    intents.presences = True
    intents.members = True
    bot = commands.Bot(
        command_prefix=BOT_COMMAND_PREFIX,
        intents=intents
    )

    @bot.listen('on_ready')
    async def on_ready(

    ) -> None:
        """
        Event listener triggered when the bot is authenticated and ready
        to run. Sets up all cogs for the application, notifies the
        guilds it is present in about its online status, and updates its
        presence.
        """
        print('Initializing HeckBot..')
        # load cogs
        await config.setup(bot)
        await gif.setup(bot)
        await poll.setup(bot)
        await react.setup(bot)

        # alert channels of bot online status
        for guild in bot.guilds:
            config.Config.config_adaptor.generate_default_config(
                bot,
                str(guild.id)
            )
            print(f'{bot.user} has connected to the following guild: '
                  f'{guild.name}(id: {guild.id})')
            if guild.id == PRIMARY_GUILD_ID:
                channel = guild.get_channel(ADMIN_CONSOLE_CHANNEL_ID)
                await channel.send(BOT_ONLINE_MESSAGE)
        await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(BOT_CUSTOM_STATUS)
        )

    @bot.listen()
    async def on_member_join(
            member: discord.Member
    ) -> None:
        """
        Event listener triggered when the bot detects a new member
        joining the guild. Sends a message in whitelisted guilds with
        a designated welcome channel to welcome the user to the guild.
        :param member: Discord member who joined
        """
        for guild in bot.guilds:
            if guild.id == PRIMARY_GUILD_ID:
                channel = guild.get_channel(WELCOME_CHANNEL_ID)
                await channel.send(WELCOME_MESSAGE.format(member.id))

    bot.run(token)


if __name__ == '__main__':
    sys.exit(main())
