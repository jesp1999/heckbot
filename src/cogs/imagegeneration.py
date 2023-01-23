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
    async def imagine(self, ctx: Context,*prompt_terms) -> None:

        # Takes a prompt and turns it into an image url
        openai.api_key=os.getenv('OPEN_API_KEY')

        prompt= ' '.join(prompt_terms)

        model='image-dALL-E-002'

        artificial_image = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url=artificial_image.data[0].url

        print(image_url)

        await ctx.send(image_url)

        # Play the sound selected with our input.

async def setup(bot: Bot) -> None:
    """
    Setup function for registering the ImageGen cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(ImageGen(bot))