import os, requests
from collections import namedtuple

from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ui import Button

import openai

ImageCacheEntry = namedtuple('ImageCacheEntry', ['user', 'channel','guild'])

class AI(commands.Cog):

    def __init__(self, bot: Bot) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        openai.api_key=os.getenv('OPEN_API_KEY')

        self._user_image_cache={}

        self._image_size='1024x1024'

        self._bot: Bot = bot

    @commands.command()
    async def imagine(self, ctx: Context,*prompt_terms) -> None:

        prompt= ' '.join(prompt_terms)

        artificial_image = openai.Image.create(
            prompt=prompt,
            n=1,
            size=self._image_size
        )

        image_url=artificial_image.data[0].url

        self._user_image_cache[ImageCacheEntry(user=ctx.author.id, channel=ctx.channel.id, guild=ctx.guild.id)]=image_url

        print(image_url)
        await ctx.send(image_url)

    @commands.command()
    async def reimagine(self, ctx: Context,*prompt_terms) -> None:

        image_url=self._user_image_cache.get(ImageCacheEntry(user=ctx.author.id, channel=ctx.channel.id, guild=ctx.guild.id))

        if image_url is None:
            await ctx.send('There\'s no previous image')
            return

        response=requests.get(image_url)
        img = response.content

        artificial_variation = openai.Image.create_variation(
                image=img,
                n=1,
                size=self._image_size
            )

        image_url=artificial_variation.data[0].url

        self._user_image_cache[ImageCacheEntry(user=ctx.author.id, channel=ctx.channel.id, guild=ctx.guild.id)]=image_url

        await ctx.send(image_url)

async def setup(bot: Bot) -> None:
    """
    Setup function for registering the ImageGen cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(AI(bot))