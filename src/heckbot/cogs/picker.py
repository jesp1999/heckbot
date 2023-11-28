from __future__ import annotations

import csv
import os
import random
import threading
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Collection
from urllib.parse import quote

from discord import ButtonStyle, Interaction, ui, InteractionResponse
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from discord.ui import Button, View
from dotenv import load_dotenv
from heckbot.utils.auth import encrypt

from bot import cursor
from bot import db_conn
from bot import HeckBot

load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')

PARTICIPANTS_MAX = 100
PARTICIPANTS_MIN = 1
RESOURCE_DIR = 'resources/'
PICK_SERVER_URL = os.getenv('PICK_SERVER_URL')

interested_activities = {}
activity_constraints = {}
last_users = []
picky_person = None
load_activities_lock = threading.Lock()


def load_activities():
    with load_activities_lock:
        global interested_activities
        interested_activities = {}
        global activity_constraints
        activity_constraints = {}
        try:
            with open(f'{RESOURCE_DIR}/games.csv') as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    if len(line) == 1:
                        activity_constraints[line[0]] = (
                            PARTICIPANTS_MIN, PARTICIPANTS_MAX
                        )
                    elif len(line) == 2:
                        activity_constraints[line[0]] = (
                            int(line[1]), PARTICIPANTS_MAX
                        )
                    else:
                        activity_constraints[line[0]] = (
                            int(line[1]), int(line[2])
                        )

            for player_file in os.listdir(f'{RESOURCE_DIR}/players/'):
                player = player_file.rpartition('.')[0]
                interested_activities[player] = set()
                with open(f'{RESOURCE_DIR}/players/' + player_file) as f:
                    interested_activities[player] = {
                        line.strip().lower() for line in f.readlines()
                    }
            print('Loaded previous data from disk')
        except Exception as ex:
            print(f'Error: {ex}')


def activities_for_users(users: list[str]) -> set[str]:
    load_activities()
    users = [user for user in users if user in interested_activities]
    r = ''
    options = interested_activities[users[0]]
    for player in users[1:]:
        options = options.intersection(interested_activities[player])
    options = {
        item for item in options
        if (
                item in activity_constraints and
                activity_constraints[item][0] <= len(users) <=
                activity_constraints[item][1]
        )
    }
    return options


def get_pick_link(user_name: str) -> str:
    ttl = 60 * 5  # 5 minutes
    expiry = (
            datetime.utcnow() + timedelta(seconds=ttl)
    ).isoformat()
    token, iv = encrypt(user_name, expiry)
    return (
            PICK_SERVER_URL +
            f'form?token={quote(token.hex())}'
            f'&iv={quote(iv.hex())}'
    )


class PickView(View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.options: set[str] = options

    @ui.button(label='Re-pick', style=ButtonStyle.green)
    async def repick(self, interaction: Interaction, button: Button):
        button.disabled = True
        if len(self.options) == 0:
            await interaction.message.edit(
                content="No options left. Y'all are too picky!",
                view=self
            )
            self.stop()
            return
        choice = random.choice(list(self.options))
        content_lines = interaction.message.content.split('\n')
        content_lines[0] = f'You can play {choice.title()}'
        content = '\n'.join(content_lines)
        self.options.remove(choice)
        button.disabled = False
        await interaction.response.edit_message(content=content, view=self)


class Picker(commands.Cog):
    """
    Cog for enabling picky-picker-related features in the bot.
    """

    def __init__(
            self,
            bot: HeckBot,
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot = bot
        self._db_conn = db_conn
        self._cursor = cursor
        load_activities()

    @commands.command()
    async def pick(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Picky Activity Picking command. The commander's voice call participants
        are used to determine which games are available to play, and a random
        game is chosen from the intersection of those games.
        :param ctx: Command context
        """
        if ctx.guild and ctx.author.voice:
            voice_states = ctx.author.voice.channel.voice_states
            users_in_channel = [
                self._bot.get_user(int(uid)) for uid in voice_states
            ]
            user_names_in_channel = [
                user.name for user in users_in_channel if not user.bot
            ]
            options = activities_for_users(user_names_in_channel)
            global picky_person
            picky_person = min(
                user_names_in_channel,
                key=lambda p: len(interested_activities.get(p, set()))
            )
            need_info_players = [
                player for player in user_names_in_channel
                if player not in interested_activities
            ]
            game = random.choice(list(options))
            options.remove(game)
            view = PickView(options)

            message_content = f'You can play {game.title()}'
            global last_users
            last_users = user_names_in_channel
            message_content += (f'\nBtw, the pickiest person here is: '
                                f'{picky_person}')
            if len(need_info_players) > 0:
                message_content += (
                    f"\n(p.s. I don't know what games these people have: "
                    f'{", ".join(need_info_players)})\n'
                )
            await ctx.send(
                message_content, view=view
            )

    @commands.command(aliases=['editpicks'])
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def edit_activity(self, ctx: Context, activity_name: str, *args):
        if len(args) == 0:
            constraints = (PARTICIPANTS_MIN, PARTICIPANTS_MAX)
        elif len(args) == 1:
            constraints = (int(args[0]), PARTICIPANTS_MAX)
        else:
            constraints = (int(args[0]), int(args[1]))
        activity_constraints[activity_name.lower()] = constraints
        with open(f'{RESOURCE_DIR}/games.csv', 'w+') as f:
            f.writelines([
                f'{game},{constraints[0]},{constraints[1]}\n'
                for game, constraints in sorted(activity_constraints.items())
            ])
        await ctx.message.add_reaction('✅')

    @commands.command(aliases=['setpicks'])
    async def set_picks(self, ctx: Context):
        await ctx.author.send(
            "Here's your custom link to edit your picks.\n"
            "Don't share this with anyone!\n" +
            get_pick_link(self._bot.get_user(ctx.author.id).name),
        )
        await ctx.message.add_reaction('📨')


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the poll cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Picker(bot))
