import os

import aiohttp
from discord.ext import commands
from discord.ext.commands import Bot, Context


class Gif(commands.Cog):
    _client_key = 'HeckBot'

    def __init__(self, bot: Bot):
        self._tenor_api_key = os.getenv('TENOR_API_KEY')
        self._bot: Bot = bot

    @commands.command()
    async def gif(self, ctx: Context, *args):
        search_term = ''.join(args)
        async with aiohttp.ClientSession() as session:
            gif_request_url = f'https://tenor.googleapis.com/v2/search?q={search_term}&key={self._tenor_api_key}' +\
                              f'&client_key={self._client_key}&limit=1'
            async with session.get(gif_request_url) as response:
                if response.status == 200:
                    response_json = await response.json()
                    gif_url = response_json['results'][0]['media_formats']['mediumgif']['url']
                    await ctx.send(gif_url)


async def setup(bot: Bot):
    await bot.add_cog(Gif(bot))
