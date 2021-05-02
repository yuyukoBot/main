import textwrap
import discord
from discord import Intents
import typing

import aiohttp

import sqlite3
from typing import Optional
from typing import Union
from datetime import time
import platform
import datetime
import time
from discord.ext import commands
import os
import functools

import inspect
from discord.ext.commands import clean_content
from discord import Embed
from discord.ext.commands import Cog
import sys
import json
import traceback
import asyncio
from discord.utils import get


def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)
POLL_CHAR = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱','🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹']

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def format_mod_embed(self, ctx, user, success, method, duration=None, location=None):
        '''Helper func to format an embed to prevent extra code'''
        emb = discord.Embed(timestamp=ctx.message.created_at)
        emb.set_author(name=method.title(), icon_url=user.avatar_url)
        emb.color = await ctx.get_dominant_color(user.avatar_url)
        emb.set_footer(text=f'User ID: {user.id}')
        if success:
            if method == 'ban' or method == 'hackban':
                emb.description = f'{user} was just {method}ned.'
            elif method == 'unmute':
                emb.description = f'{user} was just {method}d.'
            elif method == 'mute':
                emb.description = f'{user} was just {method}d for {duration}.'
            elif method == 'channel-lockdown' or method == 'server-lockdown':
                emb.description = f'`{location.name}` is now in lockdown mode!'
            else:
                emb.description = f'{user} was just {method}ed.'
        else:
            if method == 'lockdown' or 'channel-lockdown':
                emb.description = f"You do not have the permissions to {method} `{location.name}`."
            else:
                emb.description = f"You do not have the permissions to {method} {user.name}."

        with open('data/config.json') as f:
            config = json.load(f)
            modlog = os.environ.get('MODLOG') or config.get('MODLOG')
        if modlog is None:
            await ctx.send('You have not set `MODLOG` in your config vars.', delete_after=5)
        else:
            modlog = discord.utils.get(self.bot.get_all_channels(), id=int(modlog))
            if modlog is None:
                await ctx.send('Your `MODLOG` channel ID is invalid.', delete_after=5)
            else:
                await modlog.send(embed=emb)

        return emb

    @commands.command(name="kick")
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await ctx.guild.kick(user=member, reason=reason)

        # Using our past episodes knowledge can we make the log channel dynamic?
        embed = discord.Embed(
            title=f"{ctx.author.name} kicked: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    @commands.has_guild_permissions(ban_members=True)
    @commands.command(name="ban",description="ユーザーをBANします")
    async def ban(self, ctx, member_id: int, reason=None):
        """`BANの権限`"""
        embed = discord.Embed(description='ユーザーをBANしますか？')
        embed.add_field(name="対象者",value=member_id)
        mes = await ctx.send(embed=embed)
        [self.bot.loop.create_task(mes.add_reaction(i))
         for i in ("\u2705", "\u274c")]

        def check(react, usr):
            return (
                    react.message.channel == mes.channel
                    and usr == ctx.author
                    and react.message.id == mes.id
                    and react.me
            )

        reaction, user = await self.bot.wait_for('reaction_add', check=check)
        if reaction.emoji == '\u2705':
            await ctx.guild.ban(discord.Object(member_id), reason=reason)
            await ctx.send("BANしました")
        else:
            await ctx.send("キャンセルしました")

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command()
    async def delm(self, ctx, ctxid):
        """`メッセージの管理`"""
        if ctx.message.author.permissions_in(
                ctx.message.channel).manage_messages is True or ctx.author.id == 478126443168006164:
            print(
                f'{ctx.message.author.name}({ctx.message.guild.name})_' + ctx.message.content)
            dctx = await ctx.message.channel.fetch_message(ctxid)
            print(
                f'{ctx.message.author.name}さんのコマンド実行で、{ctx.message.guild.name}でメッセージ"{dctx.content}"が削除されました。')
            await dctx.delete()
            await ctx.message.delete()

    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(no_pm=True,description="banされた人が確認できます")
    async def banlist(self, ctx):
        """`BANの権限`"""
        try:
            bans = await ctx.guild.bans()
        except:
            return await ctx.send("You don't have the perms to see bans. (｡◝‿◜｡)")
        e = discord.Embed(color=0x5d00ff)
        e.set_author(name=f'List of Banned Members ({len(bans)}):', icon_url=ctx.guild.icon_url)
        result = ',\n'.join(["[" + (str(b.user.id) + "] " + str(b.user)) for b in bans])
        if len(result) < 1990:
            total = result
        else:
            total = result[:1990]
            e.set_footer(text=f'Too many bans to show here!')
        e.description = f'```bf\n{total}```'
        await ctx.send(embed=e)


    @commands.command(pass_context=True)
    @commands.has_guild_permissions(ban_members=True)
    async def unban(ctx, *, member: int = 0):
        """`メッセージの管理`"""

        if member == 0 or not isinstance(int(member),
                                         int):  # Checks if member id doesn't equal to 0 or is not an integer
            embed = discord.Embed(description=":x: Input a **Valid User ID**", color=0xff0000)
            return await commands.say(embed=embed)

        guild = ctx.message.guild  # Gets guild object
        members = get(guild.bans(),
                      id=member)  # Gets user by id in the ban list, guild.bans() is an iterable, and id is the object we need to find
        await guild.unban(user=members, reason=None)
        embed = discord.Embed(description=":white_check_mark: **%s** has been **Unbanned!**" % member.name,
                              color=0x00ff00)
        return await commands.say(embed=embed)

    @commands.bot_has_permissions(ban_members=True)
    @commands.command(aliases=['hban'],description="ユーザーをBANします",pass_context=True)
    async def hackban(self, ctx, user_id: int):
        """`BANの権限`"""
        author = ctx.message.author
        guild = author.guild

        user = guild.get_member(user_id)
        if user is not None:
            await ctx.invoke(self.ban, user=user)
            return

        try:
            await self.bot.http.ban(user_id, guild.id, 0)
            await ctx.message.edit(content=self.bot.bot_prefix + 'Banned user: %s' % user_id)
        except discord.NotFound:
            await ctx.message.edit(content=self.bot.bot_prefix + 'Could not find user. '
                                                                 'Invalid user ID was provided.')
        except discord.errors.Forbidden:
            await ctx.message.edit(content=self.bot.bot_prefix + 'Could not ban user. Not enough permissions.')

    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(name="baninfo")
    async def baninfo(self, ctx, *, name_or_id):
        """`BANの権限`"""
        ban = await ctx.get_ban(name_or_id)
        em = discord.Embed()

        em.set_author(name=str(ban.user), icon_url=ban.user.avatar_url)
        em.add_field(name='Reason', value=ban.reason or 'None')
        em.set_thumbnail(url=ban.user.avatar_url)
        em.set_footer(text=f'User ID: {ban.user.id}')

        await ctx.send(embed=em)

    @commands.command(aliases=['p', 'pl'], description='簡易的な投票機能です（引数が1つの場合と2以上の場合で動作が変わります）')
    async def poll(self, ctx, arg1=None, *args):

        usage = '/pollの使い方\n複数選択（1〜20まで）: \n `/poll 今日のランチは？ お好み焼き カレーライス`\n Yes/No: \n`/poll 明日は晴れる？`'
        msg = f'🗳 **{arg1}**'

        if arg1 is None:
            await ctx.channel.send(usage)
        elif len(args) == 0:
            message = await ctx.channel.send(msg)
            await message.add_reaction('⭕')
            await message.add_reaction('❌')
        elif len(args) > 20:
            await ctx.channel.send(f'複数選択の場合、引数は1〜20にしてください。（{len(args)}個与えられています。）')
        else:
            embed = discord.Embed(title=msg)
            for emoji, arg in zip(POLL_CHAR, args):
                embed.add_field(name=emoji, value=arg)  # inline=False

            message = await ctx.channel.send(embed=embed)

            for emoji, arg in zip(POLL_CHAR, args):
                await message.add_reaction(emoji)

    @poll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send('Missing the question.')

    @commands.command(name="poll2", aliases=["vote"], description="投票を取ることができます")
    async def quickpoll(self, ctx, *questions_and_choices: str):
        """`誰でも`"""

        if len(questions_and_choices) < 3:
            return await ctx.send('Need at least 1 question with 2 choices.')
        elif len(questions_and_choices) > 21:
            return await ctx.send('You can only have up to 20 choices.')

        perms = ctx.channel.permissions_for(ctx.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send('Need Read Message History and Add Reactions permissions.')

        question = questions_and_choices[0]
        choices = [(to_emoji(e), v) for e, v in enumerate(questions_and_choices[1:])]

        try:
            await ctx.message.delete()
        except:
            pass

        body = "\n".join(f"{key}: {c}" for key, c in choices)
        poll = await ctx.send(f'```{ctx.author} asks: {question}```\n\n{body}')
        for emoji, _ in choices:
            await poll.add_reaction(emoji)

    @commands.has_guild_permissions(manage_channels=True)
    @commands.command(name="mute", aliases=["mt"], description="ユーザーをmute")
    @commands.guild_only()
    async def mute(self, ctx, user: discord.Member, time: int = 15):
        '''```役職の管理```'''
        secs = time * 60
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                await ctx.channel.set_permissions(user, send_messages=False)
            elif isinstance(channel, discord.VoiceChannel):
                await channel.set_permissions(user, connect=False)
        e = discord.Embed(title="Mute",description=f"{user.mention} has been muted for {time} minutes.")
        await ctx.send(embed=e)
        await asyncio.sleep(secs)
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                await ctx.channel.set_permissions(user, send_messages=None)
            elif isinstance(channel, discord.VoiceChannel):
                await channel.set_permissions(user, connect=None)
        e = discord.Embed(title="Mute",description=f'{user.mention} has been unmuted from the guild')
        await ctx.send(embed=e)

    @commands.has_guild_permissions(manage_channels=True)
    @commands.command(description="```ミュートを解除```")
    @commands.guild_only()
    async def unmute(self, ctx, user: discord.Member):
        '''```役職の管理```'''
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                await ctx.channel.set_permissions(user, send_messages=None)
            elif isinstance(channel, discord.VoiceChannel):
                await channel.set_permissions(user, connect=None)

        e = discord.Embed(title="Mute",description=f'{user.mention} has been unmuted from the guild.')
        await ctx.send(embed=e)

    @commands.has_guild_permissions(manage_messages=True)
    @commands.command(name="purge", descriotion="```clearコマンドと同じです```")
    @commands.guild_only()
    async def purge(self, ctx, messages: int):
        '''`メッセージの管理`'''
        if messages > 99:
            messages = 99
        await ctx.channel.purge(limit=messages + 1)
        await ctx.send(f'{messages} messages deleted. 👌', delete_after=3)



    @commands.command(name="addrole", aliases=["ar"], description="ユーザーに役職を付与します", pass_context=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def addrole(self,ctx, member: discord.Member, *, role: discord.Role = None):
        """```メッセージの管理```"""

        await member.add_roles(role)
        e = discord.Embed(title="役職付与",description=f'{member.mention} を {role.mention}に付与した',color=0x5d00ff)
        await ctx.send(embed=e)

    @commands.has_guild_permissions(manage_roles=True)
    @commands.command(name="removerole", description="ユーザーの役職を剥奪します", pass_context=True)
    async def removerole(self,ctx, member: discord.Member, *, role: discord.Role = None):
        """```メッセージの管理```"""
        await member.remove_roles(role)
        e = discord.Embed(title="役職剥奪", description=f'{member.mention} を {role.mention}から剥奪した', color=0x5d00ff)
        await ctx.send(embed=e)

    @commands.has_guild_permissions(manage_channels=True)
    @commands.guild_only()
    @commands.command(name="slowmode", aliases=['slowmo'], description="低速モードを設定します")
    async def slowmode(self, ctx, seconds: int = 0):
        """```メッセージの管理```"""
        if seconds > 120:
            return await ctx.send(":no_entry: Amount can't be over 120 seconds")
        if seconds is 0:
            await ctx.channel.edit(slowmode_delay=seconds)
            a = await ctx.send("**Slowmode is off for this channel**")
            await a.add_reaction("a:SpectrumOkSpin:466480898049835011")
        else:
            if seconds is 1:
                numofsecs = "second"
            else:
                numofsecs = "seconds"

            await ctx.channel.edit(slowmode_delay=seconds)
            confirm = await ctx.send(
                f"**Set the channel slow mode delay to `{seconds}` {numofsecs}\nTo turn this off, do $slowmode**")
            await confirm.add_reaction("\N{THUMBS UP SIGN}")

    @commands.has_guild_permissions(manage_roles=True)
    @commands.command(aliases=["roleallmemadd", "allrole"], description="指定した役職を全メンバーに付与するよ！\n役職を管理できる人のみ！\n※BOT含む")
    async def roleallmembersadd(self,ctx, role: discord.Role):
        if (
                ctx.guild.me.top_role < ctx.author.top_role and ctx.author.guild_permissions.manage_roles) or ctx.guild.owner == ctx.author:
            embed = discord.Embed(title="操作開始", description=f"全員に{role}を付与するよ～", color=ctx.author.color,
                                  timestamp=datetime.datetime.utcnow())
            embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author.name)
            await ctx.send(embed=embed)
            [await member.add_roles(role) for member in ctx.guild.members]
            embed = discord.Embed(title="操作成功", description=f"{role}を全員に付与したよ～", color=ctx.author.color,
                                  timestamp=datetime.datetime.utcnow())
            embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author.name)
            await ctx.send(embed=embed)
        else:
            e = discord.Embed(title="実行エラー", description="君はコマンドを実行する権限を持ってないよ～", color=0xff0000)
            await ctx.send(embed=e)

    @commands.has_guild_permissions(manage_roles=True)
    @commands.command(aliases=["roleallmemremove", "roleallremove", "ramr"],description="指定した役職を全メンバーから削除するよ！\n役職を管理できる人のみ！\n※BOT含む")
    async def roleallmembersremove(self,ctx, role: discord.Role):
        if (
                ctx.guild.me.top_role < ctx.author.top_role and ctx.author.guild_permissions.manage_roles) or ctx.guild.owner == ctx.author:
            embed = discord.Embed(title="操作開始", description=f"全員から{role}を剥奪するよ～", color=ctx.author.color,
                                  timestamp=datetime.datetime.utcnow())
            embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author.name)
            await ctx.send(embed=embed)
            [await member.remove_roles(role) for member in ctx.guild.members]
            embed = discord.Embed(title="操作成功", description=f"{role}を全員から剥奪したよ～", color=ctx.author.color,
                                  timestamp=datetime.datetime.utcnow())
            embed.set_footer(icon_url=ctx.author.avatar_url, text=ctx.author.name)
            await ctx.send(embed=embed)
        else:
            e = discord.Embed(title="実行エラー", description="君はコマンドを実行する権限を持ってないよ～", color=0xff0000)
            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Moderation(bot))