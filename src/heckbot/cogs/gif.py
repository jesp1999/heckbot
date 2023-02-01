import os

import aiohttp
from discord.ext import commands
from discord.ext.commands import Bot, Context

from heckbot.service.config_service import ConfigService


class Gif(commands.Cog):
    """
    Cog for enabling gif-related features in the bot.
    """
    _client_key = 'HeckBot'

    def __init__(
            self,
            bot: Bot
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._tenor_api_key = os.getenv('TENOR_API_KEY')
        self._bot: Bot = bot

    @commands.command()
    @commands.check(ConfigService.is_enabled)
    async def gif(
            self,
            ctx: Context,
            *search_term_parts
    ) -> None:
        """
        Gif lookup command. Takes in a set of search parameters and
        queries the Tenor API for the top result for a given search,
        which is returned as an image URL sent via a Discord message in
        the same channel as the command.
        :param ctx: Command context
        :param search_term_parts: Parts of the search term as a
        collection of strings
        """
        search_term = ' '.join(search_term_parts)
        async with aiohttp.ClientSession() as session:
            # TODO refactor this to add some randomness to the returned
            #  image
            gif_request_url = (
                'https://tenor.googleapis.com/v2/'
                'search?q={}&key={}&client_key={}&limit=1').format(
                search_term,
                self._tenor_api_key,
                self._client_key
            )
            async with session.get(gif_request_url) as response:
                if response.status == 200:
                    response_json = await response.json()
                    gif_url = response_json['results'][0]['media_formats'][
                        'mediumgif']['url']
                    await ctx.send(gif_url)
                response.raise_for_status()


async def setup(
        bot: Bot
):
    """
    Setup function for registering the gif cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Gif(bot))
