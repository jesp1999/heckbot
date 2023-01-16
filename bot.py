import asyncio
import os
import discord

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
client: discord.Client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('Initializing HeckBot..')
    for guild in client.guilds:
        print(f'{client.user} has connected to the following guild: {guild.name}(id: {guild.id})')
        if guild.id == 334491082241081347:
            channel = guild.get_channel(744611387371683962)
            await channel.send('hello, i am online')


@client.event
async def on_message(message: discord.Message):
    text = message.content.lower()
    server = message.guild
    if message.author.bot:
        return

    if text[:10] == '!associate':
        args = text.split(" ")
        if len(args) != 3:
            await message.channel.send('Incorrect syntax, try \"`!associate <word> <emoji>`\"')
        else:
            word = args[1].lower()
            emoji = args[2]
            association_handler.add_association(str(server.id), word, emoji)
            await message.channel.send(f'Successfully associated the keyword \"{word}\" '
                                       f'with the reaction \"{emoji}\"!')

    if text[:11] == '!dissociate':
        args = text.split(" ")
        if len(args) == 2:
            word = args[1].lower()
            association_handler.remove_association(str(server.id), word)
            await message.channel.send(f'Successfully dissociated the keyword \"{word}\" from all reactions!')
        elif len(args) == 3:
            word = args[1].lower()
            emoji = args[2]
            association_handler.remove_association(str(server.id), word, emoji)
            await message.channel.send(f'Successfully dissociated the keyword \"{word}\" '
                                       f'with the reaction \"{emoji}\"!')
        else:
            await message.channel.send('Incorrect syntax, try \"`!dissociate <word>`\"')

    if text[:13] == "!disassociate":
        await message.channel.send('The command is \"`!dissociate`\", y\'know 😉')

    associations = association_handler.get_all_associations(str(server.id))
    for word, emojis in associations.items():
        if word in text:
            for emoji in emojis:
                asyncio.get_event_loop().create_task(message.add_reaction(emoji))


client.run(TOKEN)
