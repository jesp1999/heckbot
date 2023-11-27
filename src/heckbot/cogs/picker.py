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

from discord import ButtonStyle
from discord import Interaction
from discord import ui
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context
from discord.ui import Button
from discord.ui import View
from dotenv import load_dotenv
from heckbot.utils.auth import encrypt

from bot import cursor
from bot import db_conn
from bot import HeckBot

load_dotenv(Path(__file__).parent.parent.parent.parent / '.env')

PLAYERS_MAX = 100
PLAYERS_MIN = 1
RESOURCE_DIR = 'resources/'
PICK_SERVER_URL = os.getenv('PICK_SERVER_URL')

owned_games = {}
game_constraints = {}
last_players = []
load_game_lock = threading.Lock()


def load_games():
    with load_game_lock:
        global owned_games
        owned_games = {}
        global game_constraints
        game_constraints = {}
        global last_players
        last_players = []
        try:
            with open(f'{RESOURCE_DIR}/games.csv') as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    if len(line) == 1:
                        game_constraints[line[0]] = (PLAYERS_MIN, PLAYERS_MAX)
                    elif len(line) == 2:
                        game_constraints[line[0]] = (int(line[1]), PLAYERS_MAX)
                    else:
                        game_constraints[line[0]] = (int(line[1]), int(line[2]))

            for player_file in os.listdir(f'{RESOURCE_DIR}/players/'):
                player = player_file.rpartition('.')[0]
                owned_games[player] = set()
                with open(f'{RESOURCE_DIR}/players/' + player_file) as f:
                    owned_games[player] = {
                        line.strip().lower() for line in f.readlines()
                    }
            print('Loaded previous data from disk')
        except Exception as ex:
            print(f'Error: {ex}')


def random_game(players: list[str]) -> tuple[str, set]:
    load_games()
    need_info_players = [
        player for player in players if player not in owned_games
    ]
    players = [player for player in players if player in owned_games]
    r = ''
    options = owned_games[players[0]]
    for player in players[1:]:
        options = options.intersection(owned_games[player])
    options = {
        item for item in options
        if (
            item in game_constraints and
            game_constraints[item][0] <= len(players) <=
            game_constraints[item][1]
        )
    }
    if len(options) == 0:
        r += "No games available. Y'all are too picky."
    else:
        game_choice = random.choice(list(options))
        picky_person = min(players, key=lambda p: len(owned_games[p]))
        r = f'You can play {game_choice.title()}.'
        global last_players
        if players != last_players:
            r += f'\nBtw, the pickiest person here is: {picky_person}'
        last_players = players
    if len(need_info_players) > 0:
        r += (
            f'\n(p.s. I don\'t know what games these people have: '
            f'{", ".join(need_info_players)})\n'
        )
    return r, options


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
        super().__init__()
        self.options = options

    @ui.button(label='Confirm', style=ButtonStyle.green)
    async def repick(
        self, interaction: Interaction,
        button: Button,
    ):
        if len(self.options) == 0:
            await interaction.message.edit(
                content="No options left. Y'all are too picky!",
                view=self,
            )
            self.stop()
        choice = random.choice(self.options)
        await interaction.message.edit(content=choice, view=self)
        self.options.remove(choice)


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
        load_games()

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
            message_content, options = random_game(user_names_in_channel)
            options.remove(message_content)
            view = PickView(options)
            await ctx.send(
                message_content, view=view,
            )

    @commands.command(aliases=['editpicks'])
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True)
    async def edit_activity(self, ctx: Context, activity_name: str, *args):
        if len(args) == 0:
            constraints = (PLAYERS_MIN, PLAYERS_MAX)
        elif len(args) == 1:
            constraints = (int(args[0]), PLAYERS_MAX)
        else:
            constraints = (int(args[0]), int(args[1]))
        game_constraints[activity_name.lower()] = constraints
        with open(f'{RESOURCE_DIR}/games.csv', 'w+') as f:
            f.writelines([
                f'{game},{constraints[0]},{constraints[1]}\n'
                for game, constraints in sorted(game_constraints.items())
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
