import os
import discord
import csv

from dotenv import load_dotenv

association_file_name = "associations.csv"

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

client = discord.Client()

f = open(association_file_name, "a+")
f.close()

'''
TODO:
Reduce the number of reads to the association_file_name
Increase the specificity of bot messages to the channel
Resolve errors caused when invalid emojis are input (input validation)
'''

def get_associations():
    associations = {}
    with open(association_file_name, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 1:
                associations[row[0]] = row[1:]
    return associations

def add_association(word, emoji):
    associations = get_associations()
    if word in associations.keys():
        associations[word].append(emoji)
    else:
        associations[word] = [emoji]
    write_associations_to_file(associations)

def write_associations_to_file(associations):
    with open(association_file_name, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        for word,emojis in associations.items():
            writer.writerow([word,*emojis])

def remove_association(word, emoji=None):
    if emoji == None:
        associations = get_associations()
        associations.pop(word, None)
        write_associations_to_file(associations)
    else:
        associations = get_associations()
        if word in associations.keys() and emoji in associations[word]:
            associations[word] = [curr_emoji for curr_emoji in associations[word] if curr_emoji != emoji]
            if len(associations[word]) == 0:
                associations.pop(word)
            write_associations_to_file(associations)

associations = get_associations()

@client.event
async def on_ready():
    print("Initializing HeckBot..")
    for guild in client.guilds:
        print(f"{client.user} has connected to the following guild: {guild.name}(id: {guild.id})")

@client.event
async def on_message(message):
    global associations
    text = message.content.lower()

    if text[:10] == "!associate":
        args = text.split(" ")
        if len(args) != 3:
            await message.channel.send("Incorrect syntax, try \"`!associate <word> <emoji>`\"")
        else:
            word = args[1].lower()
            emoji = args[2]
            add_association(word, emoji)
            associations = get_associations()
            await message.channel.send(f"Successfully associated the keyword \"{word}\" with the reaction \"{emoji}\"!")

    if text[:11] == "!dissociate":
        args = text.split(" ")
        if len(args) == 2:
            word = args[1].lower()
            remove_association(word)
            associations = get_associations()
            await message.channel.send(f"Successfully dissociated the keyword \"{word}\" from all reactions!")
        elif len(args) == 3:
            word = args[1].lower()
            emoji = args[2]
            remove_association(word, emoji)
            associations = get_associations()
            await message.channel.send(f"Successfully dissociated the keyword \"{word}\" with the reaction \"{emoji}\"!")
        else:
            await message.channel.send("Incorrect syntax, try \"`!dissociate <word>`\"")

    if text[:13] == "!disassociate":
        await message.channel.send("The command is \"`!dissociate`\", y'know 😉")

    for word,emojis in associations.items():
        if word in text:
            for emoji in emojis:
                await message.add_reaction(emoji)



client.run(TOKEN)