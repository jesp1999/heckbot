from __future__ import annotations

# from typing import TYPE_CHECKING

from heckbot.utils.utils import mention

# if TYPE_CHECKING:
#     # noinspection PyUnresolvedReferences
#     from heckbot.extensions.poll import Poll

from datetime import datetime

import aiosqlite
import miru
from hikari import Embed
from hikari import Intents
from hikari import StartingEvent
from hikari import StoppingEvent
from lightbulb import BotApp
from lightbulb import CommandErrorEvent
from lightbulb.errors import CommandInvocationError, MissingRequiredRole, \
    MissingRequiredPermission, OnlyInGuild, OnlyInDM, NotEnoughArguments, \
    BotMissingRequiredPermission, MissingRequiredAttachment, CommandNotFound
from lightbulb.errors import CommandIsOnCooldown
from lightbulb import Context
from lightbulb.errors import NotOwner
from lightbulb.errors import LightbulbError
from heckbot.settings import Settings

TASK_LOOP_PERIOD = 5  # seconds

settings = Settings()

bot = BotApp(
    token=settings.bot_token,
    logs="DEBUG",
    prefix=settings.prefix,
    default_enabled_guilds=settings.declare_global_commands,
    owner_ids=settings.owner_ids,
    intents=Intents.ALL,
    help_class=None,
)


@bot.listen()
async def on_starting(event: StartingEvent):
    """Setup."""
    miru.install(bot)  # component handler
    bot.load_extensions_from("./src/heckbot/extensions")  # load extensions

    # Database setup
    bot.d.db = await aiosqlite.connect("./src/heckbot/db/database.db")
    await bot.d.db.executescript(open("./src/heckbot/db/schema.sql").read())
    await bot.d.db.commit()

    # A `dict[hikari.Message | None, UUID | None]]`
    # that maps user IDs to (task msg ID, task UUIDs).
    # Either both are `None` or both are not `None`.
    # If both are `None`, the user is not currently selecting a task.
    # TODO: Grow this on startup so we don't have
    #  to re-allocate memory every time it needs to grow
    bot.d.currently_working = {}


@bot.listen()
async def on_stopping(event: StoppingEvent):
    """Cleanup."""
    await bot.d.db.close()


async def _send_error_embed(
        content: str, exception: LightbulbError | BaseException, ctx: Context
) -> None:
    embed = Embed(
        title=f"`{exception.__class__.__name__}`"
              f" Error{f' in `/{ctx.command.name}`' if ctx.command else ''}",
        description=content,
        color=0xFF0000,
        timestamp=datetime.now().astimezone(),
    ).set_author(name=ctx.author.username, url=str(ctx.author.avatar_url))

    await ctx.respond(embed=embed)


@bot.listen(CommandErrorEvent)
async def on_error(event: CommandErrorEvent) -> None:
    """Error handler for the bot."""
    # Unwrap the exception to get the original cause
    exc = event.exception.__cause__ or event.exception
    ctx = event.context
    if not ctx.bot.rest.is_alive:
        return

    if isinstance(event.exception, CommandInvocationError):
        if not event.context.command:
            await _send_error_embed("Something went wrong", exc, ctx)
        else:
            await _send_error_embed(
                f"Something went wrong during invocation of command"
                f" `{event.context.command.name}`.", exc, ctx
            )

        raise event.exception

    # Not an owner
    if isinstance(exc, NotOwner):
        await _send_error_embed("You are not the owner of this bot.", exc, ctx)
    # Command is on cooldown
    elif isinstance(exc, CommandIsOnCooldown):
        await _send_error_embed(
            f"This command is on cooldown."
            f" Retry in `{exc.retry_after:.2f}` seconds.", exc, ctx
        )
    # Missing permissions
    elif isinstance(exc, MissingRequiredPermission):
        await _send_error_embed(
            f"You do not have permission to use this command."
            f" Missing permissions: {exc.missing_perms}", exc, ctx
        )
    # Missing roles
    elif isinstance(exc, MissingRequiredRole):
        assert event.context.guild_id is not None  # Roles only exist in guilds
        await _send_error_embed(
            f"You do not have the correct role to use this command."
            f" Missing role(s): {[mention(r, 'role')
                                  for r in exc.missing_roles]}",
            exc,
            ctx,
        )
    # Only a guild command
    elif isinstance(exc, OnlyInGuild):
        await _send_error_embed(
            "This command can only be run in servers.", exc, ctx
        )
    # Only a DM command
    elif isinstance(exc, OnlyInDM):
        await _send_error_embed(
            "This command can only be run in DMs.", exc, ctx
        )
    # Not enough arguments
    elif isinstance(exc, NotEnoughArguments):
        await _send_error_embed(
            f"Not enough arguments were supplied to the command."
            f" {[opt.name for opt in exc.missing_options]}", exc, ctx
        )
    # Bot missing permission
    elif isinstance(exc, BotMissingRequiredPermission):
        await _send_error_embed(
            f"The bot does not have the correct permission(s) to execute"
            f" this command. Missing permissions: {exc.missing_perms}",
            exc,
            ctx,
        )
    elif isinstance(exc, MissingRequiredAttachment):
        await _send_error_embed(
            "Not enough attachments were supplied to this command.", exc, ctx
        )
    elif isinstance(exc, CommandNotFound):
        await ctx.respond(
            f"`/{exc.invoked_with}` is not a valid command."
            f" Use `/help` to see a list of commands."
        )
    else:
        raise exc





# class HeckBot(commands.Bot):
#     after_ready_task: asyncio.Task[None]
#     _cogs: Final = [
#         'config',
#         'events',
#         'message',
#         'moderation',
#         'poll',
#         'react',
#         'roles',
#     ]
#
#     def __init__(self):
#         intents = Intents(
#         )
#         super().__init__(
#             command_prefix=BOT_COMMAND_PREFIX,
#             intents=intents,
#             owner_id=277859399903608834,
#             reconnect=True,
#             case_insensitive=False,
#         )
#         self.uptime = datetime.utcnow()
#         self.config = ConfigAdapter()
#
#     @tasks.loop(seconds=TASK_LOOP_PERIOD)
#     async def task_loop(self):
#         cursor.execute(
#             'SELECT rowid,* FROM tasks'
#             ' WHERE NOT completed ORDER BY end_time LIMIT 1;',
#         )
#         next_task = cursor.fetchone()
#         # if no remaining tasks, stop the loop
#         if next_task is None:
#             return
#
#         # sleep until the task should be done
#         await discord.utils.sleep_until(
#             datetime.strptime(next_task['end_time'], '%m/%d/%y %H:%M:%S'),
#         )
#         # perform task
#         task_type = next_task['task']
#         match task_type:
#             case 'close_poll':
#                 poll_cog = cast('Poll', self.get_cog('Poll'))
#                 await poll_cog.close_poll(
#                     next_task['message_id'],
#                     next_task['channel_id'],
#                 )
#             case _:  # default
#                 raise NotImplementedError
#
#         cursor.execute(
#             'UPDATE tasks SET completed = true WHERE rowid = ?;',
#             (next_task['rowid'],),
#         )
#         db_conn.commit()
#
#     def run(self, **kwargs):
#         load_dotenv(Path(__file__).parent / '.env')
#         super().run(os.environ['DISCORD_TOKEN'])
#
#     async def setup_hook(
#             self,
#     ) -> None:
#         """
#         Asynchronous setup code for the bot before gateway connection
#         :return:
#         """
#         self.after_ready_task = asyncio.create_task(self.after_ready())
#         self.task_loop.start()
#
#         self.remove_command('help')
#
#         # load extensions
#         for cog in self._cogs:
#             try:
#                 await self.load_extension(f'src.heckbot.cogs.{cog}')
#             except Exception as ex:
#                 print(f'Could not load extension {cog}: {ex}')
#                 raise ex
#
#     async def after_ready(
#             self,
#     ):
#         """
#         Asynchronous post-ready code for the bot
#         :return:
#         """
#         await self.wait_until_ready()
#
#         self.uptime = datetime.utcnow()
#
#         await self.change_presence(
#             status=discord.Status.online,
#             # TODO save this constant into a global config elsewhere
#             activity=discord.Game(BOT_CUSTOM_STATUS),
#         )
#
#         # alert channels of bot online status
#         for guild in self.guilds:
#             print(
#                 f'{self.user} has connected to the following guild: '
#                 f'{guild.name}(id: {guild.id})',
#             )
#             if guild.id == PRIMARY_GUILD_ID:
#                 channel = guild.get_channel(ADMIN_CONSOLE_CHANNEL_ID)
#                 if isinstance(channel, TextChannel):
#                     await channel.send(
#                         self.config.get_message(guild.id, 'welcomeMessage'),
#                     )
#
#         print(
#             f'----------------HeckBot---------------------'
#             f'\nBot is online as user {self.user}'
#             f'\nConnected to {(len(self.guilds))} guilds.'
#             f'\nDetected OS: {sys.platform.title()}'
#             f'\n--------------------------------------------',
#         )
#
#
# if __name__ == '__main__':
#     random.seed(0)
#     HeckBot().run()
