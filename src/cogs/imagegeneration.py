import os

from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ui import Button

import openai

class ImageGen(commands.Cog):

    def __init__(self, bot: Bot) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: Bot = bot

    @commands.command()
    async def imagine(self, ctx: Context) -> None:

        # Takes a prompt and turns it into an image url
        
        artificial_image = openai.Image.create(
        prompt=Context.fetch_message,
        model='text-davinci-003',
        api_key=os.getenv('OPEN_API_KEY')
    )

        image_url=artificial_image.data.url

        print(image_url)

        await ctx.send(image_url)

        # Play the sound selected with our input.

async def setup(bot: Bot) -> None:
    """
    Setup function for registering the ImageGen cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(ImageGen(bot))