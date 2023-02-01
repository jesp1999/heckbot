from typing import Literal

from discord.ext import commands
from discord.ext.commands import Bot, Context

from heckbot.adaptor.config_json_adaptor import ConfigJsonAdaptor

ConfigCommand = Literal[
    'add', 'create', 'update', 'set', 'remove', 'unset',
    'delete', 'get', 'read', 'load', 'list'
]


class Config(commands.Cog):
    """
    Cog for config-related features in the bot.
    """
    config_adaptor = ConfigJsonAdaptor()

    def __init__(
            self,
            bot: Bot
    ) -> None:
        """
        Constructor method
        :param bot: Instance of the running Bot
        """
        self._bot: Bot = bot

    @commands.command(aliases=['config', 'conf', 'heckbotconf',
                               'heckbotconfig'])
    # @commands.check(ConfigService.is_enabled)
    async def hbconf(
            self,
            ctx: Context[Bot],
            command: ConfigCommand,
            *config_options
    ) -> None:
        if command in ['add', 'create']:
            self.config_adaptor.save(
                str(ctx.guild.id),
                *config_options
            )
            await ctx.send(
                self.config_adaptor.load(
                    str(ctx.guild.id)
                )
            )
        elif command in ['update', 'set']:
            self.config_adaptor.save(
                str(ctx.guild.id),
                *config_options
            )
            await ctx.send(
                self.config_adaptor.load(
                    str(ctx.guild.id)
                )
            )
        elif command in ['remove', 'unset', 'delete']:
            self.config_adaptor.save(
                str(ctx.guild.id),
                *config_options,
                None
            )
            await ctx.send(
                self.config_adaptor.load(
                    str(ctx.guild.id)
                )
            )
        elif command in ['get', 'read', 'load']:
            await ctx.send(
                self.config_adaptor.load(
                    str(ctx.guild.id),
                    *config_options
                )
            )
        elif command == 'list':
            await ctx.send(
                self.config_adaptor.load(
                    str(ctx.guild.id),
                    *config_options
                )
            )


async def setup(
        bot: Bot
) -> None:
    """
    Setup function for registering the gif cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Config(bot))
