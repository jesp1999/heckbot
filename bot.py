import os
from os.path import join, dirname

import discord
from discord.ext import commands

from dotenv import load_dotenv

from src.cogs import reactmatch, poll, gif

load_dotenv(join(dirname(__file__), '.env'))

TOKEN: str = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.typing = True
intents.presences = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.listen('on_ready')
async def on_ready():
    print('Initializing HeckBot..')
    # load cogs
    await reactmatch.setup(bot)
    await poll.setup(bot)
    await gif.setup(bot)

    # alert channels of bot online status
    for guild in bot.guilds:
        print(f'{bot.user} has connected to the following guild: {guild.name}(id: {guild.id})')
        if guild.id == 334491082241081347:
            channel = guild.get_channel(744611387371683962)
            await channel.send('hello, i am online')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game('the part :)')
    )


# welcome message in channel
@bot.listen()
async def on_member_join(member):
    # essentially whitelisted servers with a designated channel; we can either give the bot permission to make a channel
    # so we could allow that on any server, or add whitelisted servers as wanted
    for guild in bot.guilds:
        if guild.id == 334491082241081347:
            # placeholder channel; we need a welcome channel in HeckBoiCrue
            channel = guild.get_channel(744611387371683962)
            # the actual message; edit as wanted. if we allow bot to be in more servers we will have to make a command
            # to change the message we want to send per server
            await channel.send(f"Welcome to HeckBoiCrue <@!{member.id}>!")

#welcome message dm
@bot.listen()
async def on_member_join(member):
        await member.send(f"Welcome to HeckBoiCrue!")

bot.run(TOKEN)
