from __future__ import annotations

import csv
import os
import random

from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from bot import cursor
from bot import db_conn
from bot import HeckBot

PLAYERS_MAX = 100
PLAYERS_MIN = 1
RESOURCE_DIR = 'resources/'


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
        self._owned_games = {}
        self._game_constraints = {}
        self._last_players = []
        self.load_games()

    @commands.command()
    async def pick(
            self,
            ctx: Context[Bot],
    ) -> None:
        """
        Polling command. The commander specifies the poll duration, poll
        question, and answers as space-delimited strings which may
        contain spaces as long as they are within quotes. If the
        commander only specifies the poll question, the answers will be
        assumed to be yes/no.
        :param ctx: Command context
        """
        if ctx.guild and ctx.author.voice:
            voice_states = ctx.author.voice.channel.voice_states
            users_in_channel = [
                self._bot.get_user(int(uid)).name for uid in voice_states
            ]
            await ctx.send(self.random_game(users_in_channel))

    def load_games(self):
        try:
            with open(f'{RESOURCE_DIR}/games.csv') as f:
                csv_reader = csv.reader(f)
                for line in csv_reader:
                    if len(line) == 1:
                        self._game_constraints[line[0]] = (PLAYERS_MIN, PLAYERS_MAX)
                    elif len(line) == 2:
                        self._game_constraints[line[0]] = (
                            int(line[1]), PLAYERS_MAX
                        )
                    else:
                        self._game_constraints[line[0]] = (
                            int(line[1]), int(line[2])
                        )

            for player_file in os.listdir(f'{RESOURCE_DIR}/players'):
                player = player_file.rpartition('.')[0]
                self._owned_games[player] = set()
                with open(f'{RESOURCE_DIR}/players/' + player_file) as f:
                    self._owned_games[player] = {line.strip().lower() for line in f.readlines()}
            print('Loaded previous data from disk')
        except Exception as ex:
            print('Nothing to load from disk')
            ...

    def random_game(self, players: list[str]):
        need_info_players = [
            player for player in players if player not in self._owned_games
        ]
        players = [player for player in players if player in self._owned_games]
        r = ''
        options = self._owned_games[players[0]]
        for player in players[1:]:
            options = options.intersection(self._owned_games[player])
        options = {
            item for item in options
            if self._game_constraints[item][0] <= len(players) <= self._game_constraints[item][1]
        }
        if len(options) == 0:
            r += "No games available. Y'all are too picky."
        else:
            game_choice = random.choice(list(options))
            picky_person = min(players, key=lambda p: len(self._owned_games[p]))
            r = f'You can play {game_choice}.'
            if players != self._last_players:
                r += f'\nBtw, the pickiest person here is: {picky_person}'
            self._last_players = players
        if len(need_info_players) > 0:
            r += (
                f'\n(p.s. I don\'t know what games these people have: '
                f'{", ".join(need_info_players)})\n'
            )
        return r


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the poll cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Picker(bot))
