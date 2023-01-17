from discord.ext import commands
from discord.ext.commands import Bot, Context


class Poll(commands.Cog):
    _yes_no_reactions = ['👍', '👎']
    _multi_choice_reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.command()
    async def poll(self, ctx: Context, *args):
        poll_args = ''.join(args).split('"')
        poll_args = [poll_arg for poll_arg in poll_args if poll_arg not in ['', ' ']]
        if len(poll_args) == 1:
            # Yes/no poll
            question = poll_args[0]
            if question[:2] != '**' or question[-2:] != '**':
                question = '**' + question + '**'

            message = await ctx.send(question)
            for reaction in self._yes_no_reactions:
                await message.add_reaction(reaction)
        elif len(poll_args) > 1:
            # Multi-choice poll
            question = poll_args[0]
            choices = poll_args[1:]
            if question[:2] != '**' or question[-2:] != '**':
                question = '**' + question + '**'
            num_choices = len(poll_args) - 1
            message = await ctx.send(question + '\n' + '\n'.join(choices))
            # TODO handle more poll options than emojis in list
            for reaction in self._multi_choice_reactions[:num_choices]:
                await message.add_reaction(reaction)
        else:
            await ctx.send('Incorrect syntax, try \"`!poll "<question>" "[choice1]" "[choice2]" ...`\"')


async def setup(bot):
    await bot.add_cog(Poll(bot))
