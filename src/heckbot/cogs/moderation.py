from __future__ import annotations

import traceback

import discord
import logging
from discord import Embed
from discord import Member
from discord import Role
from discord import TextChannel
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Context

from bot import HeckBot

logger = logging.getLogger(__name__)


class Moderation(commands.Cog):
    def __init__(
            self,
            bot: HeckBot,
    ):
        self._bot = bot

    def embed_for_message(
            self,
            guild_id: int,
            message: str,
    ) -> Embed:
        return Embed(
            color=self._bot.config.get_color(guild_id, 'embedColor'),
            title='Error',
            description=message,
        )

    # @commands.command(aliases=['addrole'])
    # @commands.has_permissions(manage_roles=True)
    # @commands.bot_has_permissions(manage_roles=True)
    # async def add_role(
    #         self,
    #         ctx: Context[Bot],
    #         role: Role,
    #         member: Member,
    # ) -> None:
    #     if ctx.guild is None or not isinstance(ctx.author, Member):
    #         return
    #     if ctx.guild.me.top_role < member.top_role:
    #         await ctx.send(
    #             embed=self.embed_for_message(
    #                 ctx.guild.id,
    #                 'higherPermissionErrorMessage',
    #             ),
    #         )
    #     elif ctx.author.top_role == member.top_role:
    #         await ctx.send(
    #             embed=self.embed_for_message(
    #                 ctx.guild.id,
    #                 'equalPermissionErrorMessage',
    #             ),
    #         )
    #     elif ctx.guild.me.top_role > member.top_role:
    #         await member.add_roles(role)
    #         await ctx.send(
    #             embed=discord.Embed(
    #                 color=self._bot.config.get_color(
    #                     ctx.guild.id,
    #                     'embedColor',
    #                 ),
    #                 title='Success',
    #                 description=f'{member.mention} has been granted the role '
    #                             f'`{role}`',
    #             ),
    #         )
    #     else:
    #         traceback.print_exc()

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
            self,
            ctx: Context[Bot],
            member: Member,
            *,
            reason='No reason provided!',
    ) -> None:
        if ctx.guild is None or not isinstance(ctx.author, Member):
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send(
                embed=self.embed_for_message(
                    ctx.guild.id,
                    'higherPermissionErrorMessage',
                ),
            )
        elif ctx.author.top_role <= member.top_role:
            await ctx.send(
                embed=self.embed_for_message(
                    ctx.guild.id,
                    'equalPermissionErrorMessage',
                ),
            )
        elif ctx.guild.me.top_role > member.top_role:
            embed = discord.Embed(
                color=self._bot.config.get_color(
                    ctx.guild.id,
                    'embedColor',
                ),
                title='Success',
                description=f'{member.mention} has been banned.',
            )

            sender = ctx.author
            await member.ban(reason=reason)

            await ctx.send(embed=embed)

            embed2 = discord.Embed(
                color=self._bot.config.get_color(
                    ctx.guild.id,
                    'embedColor',
                ),
                title=f'{member} → You Have Been Banned!',
            )
            embed2.add_field(name='• Moderator', value=f'{sender}')
            embed2.add_field(name='• Reason', value=f'{reason}')
            embed2.set_footer(text=f'Banned from: {ctx.guild}')

            await member.send(embed=embed2)
        else:
            traceback.print_exc()

    @commands.command(aliases=['forceban'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def force_ban(
            self,
            ctx: Context[Bot],
            *,
            member_id: int,
    ) -> None:
        if ctx.guild is None:
            return
        await ctx.guild.ban(discord.Object(member_id))
        await ctx.send(
            embed=discord.Embed(
                color=self._bot.config.get_color(
                    ctx.guild.id,
                    'embedColor',
                ),
                title='Success',
                description=f'<@{member_id}> has been forcefully banned.',
            ),
        )

    @commands.command(pass_context=True)
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
            self,
            ctx: Context[Bot],
            member: Member,
            *,
            reason='No reason provided!',
    ) -> None:
        if ctx.guild is None or not isinstance(ctx.author, Member):
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send(
                embed=self.embed_for_message(
                    ctx.guild.id,
                    'higherPermissionErrorMessage',
                ),
            )
        elif ctx.author.top_role <= member.top_role:
            await ctx.send(
                embed=self.embed_for_message(
                    ctx.guild.id,
                    'equalPermissionErrorMessage',
                ),
            )
        elif ctx.guild.me.top_role > member.top_role:
            sender = ctx.author
            await member.kick(reason=reason)
            await ctx.send(
                embed=discord.Embed(
                    color=self._bot.config.get_color(
                        ctx.guild.id,
                        'embedColor',
                    ),
                    title='Success',
                    description=f'{member.mention} has been kicked.',
                ),
            )
            embed = discord.Embed(
                color=self._bot.config.get_color(
                    ctx.guild.id,
                    'embedColor',
                ),
                title=f'{member}, you have been kicked.',
            )
            embed.add_field(name='Moderator', value=f'{sender}')
            embed.add_field(name='Reason', value=f'{reason}')
            embed.set_footer(text=f'Kicked from: {ctx.guild}')
            await member.send(embed=embed)
        else:
            traceback.print_exc()

    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nickname(
            self,
            ctx: Context[Bot],
            member: Member,
            *,
            nickname: str,
    ) -> None:
        if ctx.guild is None or not isinstance(ctx.author, Member):
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send(
                embed=self.embed_for_message(
                    ctx.guild.id,
                    'higherPermissionErrorMessage',
                ),
            )
        elif ctx.author.top_role <= member.top_role:
            await ctx.send(
                embed=self.embed_for_message(
                    ctx.guild.id,
                    'equalPermissionErrorMessage',
                ),
            )
        elif ctx.guild.me.top_role > member.top_role:
            await member.edit(nick=nickname)
            embed = discord.Embed(
                color=self._bot.config.get_color(
                    ctx.guild.id,
                    'embedColor',
                ),
                title='Success',
                description=f"{member.mention}'s nickname has been changed.",
            )
            await ctx.send(embed=embed)
        else:
            traceback.print_exc()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(
            self,
            ctx: Context[Bot],
            amount: int,
    ) -> None:
        if ctx.guild is None or not isinstance(ctx.channel, TextChannel):
            return
        await ctx.channel.purge(limit=amount)

    # @commands.command(aliases=['removerole', 'delrole'])
    # @commands.has_permissions(manage_roles=True)
    # @commands.bot_has_permissions(manage_roles=True)
    # async def remove_role(
    #         self,
    #         ctx: Context[Bot],
    #         role: Role,
    #         member: Member,
    # ) -> None:
    #     if ctx.guild is None or not isinstance(ctx.author, Member):
    #         return
    #     if ctx.guild.me.top_role < member.top_role:
    #         await ctx.send(
    #             embed=self.embed_for_message(
    #                 ctx.guild.id,
    #                 'higherPermissionErrorMessage',
    #             ),
    #         )
    #     elif ctx.author.top_role <= member.top_role:
    #         await ctx.send(
    #             embed=self.embed_for_message(
    #                 ctx.guild.id,
    #                 'equalPermissionErrorMessage',
    #             ),
    #         )
    #     elif ctx.guild.me.top_role > member.top_role:
    #         await member.remove_roles(role)
    #         await ctx.send(
    #             embed=discord.Embed(
    #                 color=self._bot.config.get_color(
    #                     ctx.guild.id,
    #                     'embedColor',
    #                 ),
    #                 title='Success',
    #                 description=f'{member.mention} lost the role `{role}`.',
    #             ),
    #         )
    #     else:
    #         traceback.print_exc()

    @commands.command(aliases=['resetnick', 'resetnickname', 'reset_nickname'])
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def reset_nick(
            self,
            ctx: Context[Bot],
            member: Member,
    ) -> None:
        if ctx.guild is None or not isinstance(
            ctx.author, Member,
        ):
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send(
                embed=self.embed_for_message(
                    ctx.guild.id,
                    'higherPermissionErrorMessage',
                ),
            )
        elif ctx.author.top_role <= member.top_role:
            await ctx.send(
                embed=self.embed_for_message(
                    ctx.guild.id,
                    'equalPermissionErrorMessage',
                ),
            )
        elif ctx.guild.me.top_role > member.top_role:
            await member.edit(nick=None)
            await ctx.send(
                embed=discord.Embed(
                    color=self._bot.config.get_color(
                        ctx.guild.id,
                        'embedColor',
                    ),
                    title='Success',
                    description=f"{member.mention}'s nickname has been reset.",
                ),
            )
        else:
            traceback.print_exc()

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(
            self,
            ctx: Context[Bot],
            *,
            member_id: int,
    ) -> None:
        if ctx.guild is None:
            return
        await ctx.guild.unban(discord.Object(member_id))
        embed = discord.Embed(
            color=self._bot.config.get_color(
                ctx.guild.id,
                'embedColor',
            ),
            title='Success',
            description=f'<@{member_id}> has been unbanned.',
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def warn(
            self,
            ctx: Context[Bot],
            member: Member,
            *,
            reason: str = 'No reason provided!',
    ) -> None:
        if ctx.guild is None:
            return
        if ctx.guild.me.top_role < member.top_role:
            await ctx.send(
                'Error: The specified user has higher permissions than you.',
            )
        elif ctx.guild.me.top_role > member.top_role:
            sender = ctx.author
            await ctx.send(
                embed=discord.Embed(
                    color=self._bot.config.get_color(
                        ctx.guild.id,
                        'embedColor',
                    ),
                    title='Success',
                    description=f'{member.mention} has been warned.',
                ),
            )
            embed = discord.Embed(
                color=self._bot.config.get_color(
                    ctx.guild.id,
                    'embedColor',
                ),
                title=f'{member}, you have been warned.',
            )
            embed.add_field(name='Moderator', value=f'`{sender}`')
            embed.add_field(name='Reason', value=f'`{reason}`')
            embed.set_footer(text=f'Warning sent from: {ctx.guild}')
            await member.send(embed=embed)


async def setup(
        bot: HeckBot,
) -> None:
    """
    Setup function for registering the poll cog.
    :param bot: Instance of the running Bot
    """
    await bot.add_cog(Moderation(bot))
