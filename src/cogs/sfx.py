from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ui import Button



class Sfx(commands.Cog):

    def __init__(self, bot: Bot) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: Bot = bot

    @commands.command()
    async def playsound(self, ctx: Context, *search_term_parts) -> None:

        # Simple check to make sure the user is actually inside of a voice channel.

        user_vc = ctx.author.voice.channel
        if user_vc is None:
            await ctx.send('*You aren\'t in a voice channel.*')
            return
    
        # Connect to the user's voice channel
        
        voice_client = await user_vc.connect()

        # Play the sound selected with our input.

        voice_client.play()
        return

async def setup(bot: Bot) -> None:
    """
    Setup function for registering the sfx cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Sfx(bot))