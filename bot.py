import asyncio
import os
import discord
from discord.ext import commands
from discord.ext.commands import Context

from dotenv import load_dotenv
from src.handler.association_handler import AssociationHandler


load_dotenv()

association_handler: AssociationHandler = AssociationHandler()
TOKEN: str = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.typing = True
intents.presences = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.listen('on_ready')
async def on_ready():
    print('Initializing HeckBot..')
    for guild in bot.guilds:
        print(f'{bot.user} has connected to the following guild: {guild.name}(id: {guild.id})')
        if guild.id == 334491082241081347:
            channel = guild.get_channel(744611387371683962)
            await channel.send('hello, i am online')


@bot.command()
async def associate(ctx: Context, *args):
    if len(args) != 2:
        await ctx.send('Incorrect syntax, try \"`!associate <word> <emoji>`\"')
    else:
        word = args[0].lower()
        emoji = args[1]
        association_handler.add_association(str(ctx.guild.id), word, emoji)
        await ctx.send(f'Successfully associated the keyword \"{word}\" with the reaction \"{emoji}\"!')


@bot.command()
async def dissociate(ctx: Context, *args):
    if len(args) == 1:
        word = args[0].lower()
        association_handler.remove_association(str(ctx.guild.id), word)
        await ctx.send(f'Successfully dissociated the keyword \"{word}\" from all reactions!')
    elif len(args) == 2:
        word = args[0].lower()
        emoji = args[1]
        association_handler.remove_association(str(ctx.guild.id), word, emoji)
        await ctx.send(f'Successfully dissociated the keyword \"{word}\" with the reaction \"{emoji}\"!')
    else:
        await ctx.send('Incorrect syntax, try \"`!dissociate <word>`\"')


@bot.command()
async def disassociate(ctx: Context, *args):
    await ctx.send('The command is \"`!dissociate`\", y\'know 😉')


@bot.listen('on_message')
async def on_message(message: discord.Message):
    text = message.content.lower()
    server = message.guild
    if message.author.bot or (await bot.get_context(message)).valid:
        return

    associations = association_handler.get_all_associations(str(server.id))
    for word, emojis in associations.items():
        if word in text:
            for emoji in emojis:
                asyncio.get_event_loop().create_task(message.add_reaction(emoji))


bot.run(TOKEN)
