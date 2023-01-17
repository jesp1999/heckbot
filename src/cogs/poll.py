from discord.ext import commands
from discord.ext.commands import Bot, Context


class Poll(commands.Cog):
    _yes_no_reactions = ['👍', '👎']
    _multi_choice_reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.command()
    async def poll(self, ctx: Context, *args):
        if len(args) == 1:
            # Yes/no poll
            question = args[0]
            if question[:2] != '**' or question[-2:] != '**':
                question = '**' + question + '**'

            message = await ctx.send(question)
            for reaction in self._yes_no_reactions:
                await message.add_reaction(reaction)
        elif len(args) > 1:
            # Multi-choice poll
            question = args[0]
            choices = args[1:]
            if question[:2] != '**' or question[-2:] != '**':
                question = '**' + question + '**'
            num_choices = len(args) - 1
            message_text = question
            for i in range(num_choices):
                message_text += f'\n{self._multi_choice_reactions[i]}: {choices[i]}'
            message = await ctx.send(message_text)
            # TODO handle more poll options than emojis in list
            for reaction in self._multi_choice_reactions[:num_choices]:
                await message.add_reaction(reaction)
        else:
            await ctx.send('Incorrect syntax, try \"`!poll "<question>" "[choice1]" "[choice2]" ...`\"')


async def setup(bot):
    await bot.add_cog(Poll(bot))
