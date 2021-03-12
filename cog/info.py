import textwrap
from discord import Intents
import typing
from datetime import time
import aiohttp
import datetime
from datetime import datetime, timedelta
from typing import Optional

from typing import Union
import time, struct,subprocess

import platform
from discord.ext import commands
from platform import python_version
from discord import __version__ as discord_version
from asyncio import sleep
from cog import ProgressBar,DisplayName
from discord.utils import get

from collections import OrderedDict, deque, Counter
import datetime
import time
import os

import asyncio, discord
import random
import secrets
from io import BytesIO
import ast
import psutil
import functools
import inspect
import DiscordUtils
from discord.ext.commands import clean_content
from discord import Embed
from discord.ext.commands import Cog
import sys
import json
import traceback
import wikipedia
import io
from contextlib import redirect_stdout
import re

import tracemalloc
from cog import UserTime



class infoCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _getRoles(roles):
        string = ''
        for role in roles[::-1]:
            if not role.is_default():
                string += f'{role.mention}, '
        if string == '':
            return 'None'
        else:
            return string[:-2]

    @staticmethod
    def _getEmojis(emojis):
        string = ''
        for emoji in emojis:
            string += str(emoji)
        if string == '':
            return 'None'
        else:
            return string[:1000]  # The maximum allowed charcter amount for embed fields

    @commands.command(aliases=["si"], name="serverinfo", usage='')
    @commands.guild_only()
    async def guildinfo(self, ctx, *, guild_id: int = None):
        """Shows info about the current server."""

        if guild_id is not None and await self.bot.is_owner(ctx.author):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return await ctx.send(f'Invalid Guild ID given.')
        else:
            guild = ctx.guild

        if not guild.chunked:
            async with ctx.typing():
                await guild.chunk(cache=True)

        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1

        e = discord.Embed(title="サーバー情報", color=0x5d00ff)
        e.add_field(name="サーバー名", value=f'{guild.name}({guild.id})')
        e.add_field(name="Owner", value=guild.owner)

        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        bm = 0
        ubm = 0
        for m in guild.members:
            if m.bot:
                bm = bm + 1
            else:
                ubm = ubm + 1
        e.add_field(name="メンバー数",
                    value=f"{len(guild.members)}(<:bot:798877222638845952>:{bm}/:busts_in_silhouette::{ubm})")
        e.add_field(name="チャンネル数",
                    value=f'{("<:categorie:798883839124308008>")}:{len(guild.categories)}\n{(":speech_balloon:")}:{len(guild.text_channels)}\n{(":mega:")}:{len(guild.voice_channels)}')

        e.add_field(name="絵文字", value=len(guild.emojis))
        e.add_field(name="地域", value=str(guild.region))
        e.add_field(name="認証度", value=str(guild.verification_level))
        if guild.afk_channel:
            e.add_field(name="AFKチャンネル", value=f"{guild.afk_channel.name}({str(guild.afk_channel.id)})")
            e.add_field(name="AFKタイムアウト", value=str(guild.afk_timeout / 60))

        if guild.system_channel:
            e.add_field(name="システムチャンネル", value=f"{guild.system_channel}\n({str(guild.system_channel.id)})")
        try:

            e.add_field(name="welcome", value=guild.system_channel_flags.join_notifications)
            e.add_field(name="boost", value=guild.system_channel_flags.premium_subscriptions)
        except:
            pass
        if guild.afk_channel:
            e.add_field(name="AFKチャンネル", value=f"{guild.afk_channel.name}({str(guild.afk_channel.id)})")
            e.add_field(name="AFKタイムアウト", value=str(guild.afk_timeout / 60))
        else:
            e.add_field(name="AFKチャンネル", value="設定されていません")

        if "INVITE_SPLASH" in ctx.guild.features:
            e.add_field(name="招待の背景画像",
                        value="下に表示")
            e.set_image(url=ctx.guild.splash_url_as(format="png"))

        if "BANNER" in ctx.guild.features:
            e.add_field(name="バナー",
                        value="下に表示")
            e.set_thumbnail(url=ctx.guild.banner_url_as(format="png"))

        emojis = self._getEmojis(guild.emojis)

        e.add_field(name='カスタム絵文字', value=emojis, inline=False)

        roles = self._getRoles(guild.roles)
        if len(roles) <= 1024:
            e.add_field(name="役職", value=roles, inline=False)
        else:
            e.add_field(name="役職", value="多いですよ")

        e1 = discord.Embed(title="manage")
        if guild.verification_level == discord.VerificationLevel.none:
            e1.add_field(name="認証レベル", value="なし")

        elif guild.verification_level == discord.VerificationLevel.low:
            e1.add_field(name="認証レベル",
                         value="メール認証済み")
        elif guild.verification_level == discord.VerificationLevel.medium:
            e1.add_field(name="認証レベル",
                         value="メール認証済みかつアカウント作成から5分経過")
        elif guild.verification_level == discord.VerificationLevel.high:
            e1.add_field(name="認証レベル",
                         value="メール認証済みかつアカウント作成から5分経過かつサーバー参加後10分経過")
        elif guild.verification_level == discord.VerificationLevel.extreme:
            e1.add_field(name="認証レベル",
                         value="電話番号による認証済み")

        if guild.explicit_content_filter == discord.ContentFilter.disabled:
            e1.add_field(name="不適切な表現のフィルター",
                         value="使用しない")
        elif guild.explicit_content_filter == discord.ContentFilter.no_role:
            e1.add_field(name="不適切な表現のフィルター",
                         value="役職を持たないメンバー")
        elif guild.explicit_content_filter == discord.ContentFilter.all_members:
            e1.add_field(name="不適切な表現のフィルター",
                         value="すべてのメンバー")

        e2 = discord.Embed(title="サーバー情報")
        if ctx.author.guild_permissions.manage_roles or ctx.author.id == 478126443168006164:
            rl = guild.roles[::-1]
            rls = ""
            for r in rl:
                if len(f"{rls}\n{r.name}") >= 1998:
                    rls = rls + "\n…"
                    break
                else:
                    rls = f"{rls}\n{r.name}"
            e2.add_field(name="役職", value=rls)
        else:
            e2.add_field(name="役職", value="権限がありません")

        e3 = discord.Embed(title="サーバー情報")
        if ctx.author.guild_permissions.manage_guild or ctx.author.id == 478126443168006164:
            try:
                wdt = await guild.widget()
                e3.add_field(name="ウィジェット", value=f"URL: {wdt.json_url}")

            except:
                e3.add_field(name="ウィジェット", value="ウィジェットは無効です。")

        else:
            e3.add_field(name="ウィジェット", value="権限がありません")

        e4 = discord.Embed(title="サーバー情報",
                           description=f"Level:{guild.premium_tier}\n({guild.premium_subscription_count})")
        e4.add_field(name="ブーストの追加要素",
                     value=f"ginfo-blev{guild.premium_tier}")
        e.add_field(name="features",
                    value=f"```{','.join(guild.features)}```")

        vml = "ginfo-strlenover"
        if len("\n".join([f"{str(i)}" for i in guild.members])) <= 1024:
            vml = "\n".join([f"{str(i)}" for i in guild.members]).replace(
                str(ctx.guild.owner), f"👑{str(ctx.guild.owner)}")

        e5 = discord.Embed(title="メンバー", description=f"member count:{len(guild.members)}\n```" + vml + "```")

        e.add_field(name="features",
                    value=f"```{','.join(guild.features)}```")

        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
        paginator.add_reaction('<:outline_fast_rewind_black_24dp:809040685881229373>', "first")
        paginator.add_reaction('<:arrowleftbox:809036770070233088>', "back")
        paginator.add_reaction('<:lockopen:809045312952991755>', "lock")
        paginator.add_reaction('<:arrowrightbox1:809038120678326273>', "next")
        paginator.add_reaction('<:outline_fast_forward_black_24dp:809040782358347778>', "last")
        embeds = [e, e1, e2, e3, e4, e5]
        await paginator.run(embeds)

    @commands.command()
    async def server(self, ctx, *, guild_name=None):
        """Lists some info about the current or passed server."""

        # Check if we passed another guild
        guild = None
        if guild_name == None:
            guild = ctx.guild
        else:
            for g in self.bot.guilds:
                if g.name.lower() == guild_name.lower():
                    guild = g
                    break
                if str(g.id) == str(guild_name):
                    guild = g
                    break
        if guild == None:
            # We didn't find it
            await ctx.send("I couldn't find that guild...")
            return

        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1
        e = discord.Embed(title="サーバー情報", color=0x0066ff)

        e.add_field(name="サーバー名", value=f'{guild.name}({guild.id})')
        e.add_field(name="Owner", value=guild.owner)

        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        bm = 0
        ubm = 0
        for m in guild.members:
            if m.bot:
                bm = bm + 1
            else:
                ubm = ubm + 1
        e.add_field(name="メンバー数",
                    value=f"{len(guild.members)}(<:bot:798877222638845952>:{bm}/:busts_in_silhouette::{ubm})")
        e.add_field(name="チャンネル数",
                    value=f'{("<:categorie:798883839124308008>")}:{len(guild.categories)}\n{(":speech_balloon:")}:{len(guild.text_channels)}\n{(":mega:")}:{len(guild.voice_channels)}')

        e.add_field(name="絵文字", value=len(guild.emojis))
        e.add_field(name="地域", value=str(guild.region))
        e.add_field(name="認証度", value=str(guild.verification_level))
        if guild.afk_channel:
            e.add_field(name="AFKチャンネル", value=f"{guild.afk_channel.name}({str(guild.afk_channel.id)})")
            e.add_field(name="AFKタイムアウト", value=str(guild.afk_timeout / 60))

        if guild.system_channel:
            e.add_field(name="システムチャンネル", value=f"{guild.system_channel}\n({str(guild.system_channel.id)})")
        try:

            e.add_field(name="welcome", value=guild.system_channel_flags.join_notifications)
            e.add_field(name="boost", value=guild.system_channel_flags.premium_subscriptions)
        except:
            pass
        if guild.afk_channel:
            e.add_field(name="AFKチャンネル", value=f"{guild.afk_channel.name}({str(guild.afk_channel.id)})")
            e.add_field(name="AFKタイムアウト", value=str(guild.afk_timeout / 60))

        emojis = self._getEmojis(guild.emojis)

        e.add_field(name='カスタム絵文字', value=emojis, inline=False)

        roles = self._getRoles(guild.roles)
        if len(roles) <= 1024:
            e.add_field(name="役職", value=roles, inline=False)
        else:
            e.add_field(name="役職", value="多いですよ")

        await ctx.send(embed=e)

    @commands.command()
    async def debug(self, ctx):
        mem = psutil.virtual_memory()
        allmem = str(mem.total / 1000000000)[0:3]
        used = str(mem.used / 1000000000)[0:3]
        ava = str(mem.available / 1000000000)[0:3]
        memparcent = mem.percent

        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        e = discord.Embed(title="ステータス",
                          url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=1024",
                          color=0x5d00ff)
        e.add_field(name="プロセッサ", value="Intel(R) Core(TM) i7 CPU")
        e.add_field(name="discord.pyのバージョン", value=dpyVersion)
        e.add_field(name="Pythonのバージョン", value=pythonVersion)
        e.add_field(name="OS", value=f"```{platform.system()} {platform.release()}({platform.version()})```")
        e.add_field(
            name="メモリ",
            value=f"```全てのメモリ容量:{allmem}GB\n使用量:{used}GB({memparcent}%)\n空き容量{ava}GB({100 - memparcent}%)```")

        await ctx.send(embed=e)

    @commands.command(name="info")
    async def info(self, ctx):

        """`誰でも`"""

        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        channels = str(len(set(self.bot.get_all_channels())))
        total_members = [x.id for x in self.bot.get_all_members()]
        unique_members = set(total_members)
        if len(total_members) == len(unique_members):
            member_count = "{:,}".format(len(total_members))
        else:
            member_count = "{:,} ({:,} unique)".format(len(total_members), len(unique_members))

        guild_count = "{:,}".format(len(self.bot.guilds))

        cog_amnt = 0
        empty_cog = 0
        for cog in self.bot.cogs:
            visible = []
            for c in self.bot.get_cog(cog).get_commands():
                if c.hidden:
                    continue
                visible.append(c)
            if not len(visible):
                empty_cog += 1
                # Skip empty cogs
                continue
            cog_amnt += 1

        cog_count = "{:,} cog".format(cog_amnt)
        # Easy way to append "s" if needed:
        if not len(self.bot.cogs) == 1:
            cog_count += "s"
        if empty_cog:
            cog_count += " [{:,} without commands]".format(empty_cog)

        visible = []
        for command in self.bot.commands:
            if command.hidden:
                continue
            visible.append(command)

        command_count = "{:,}".format(len(visible))

        embed = discord.Embed(title="幽々子",
                              url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=1024",
                              color=0x5d00ff)
        embed.set_author(name="y/info")

        embed.add_field(name="サーバー数", value=guild_count)
        embed.add_field(name="ユーザー数", value=member_count)
        embed.add_field(name="command", value=command_count + " (in {})".format(cog_count))

        embed.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=1024")
        embed.add_field(name="Channels bot can see:", value=channels)
        embed.add_field(name="discord.pyのバージョン", value=dpyVersion)
        embed.add_field(name="Pythonのバージョン", value=pythonVersion)
        embed.add_field(name="導入",
                        value="https://discord.com/api/oauth2/authorize?client_id=757807145264611378&permissions=0&scope=bot")

        embed.set_footer(text="何かあればButachaan#0001まで")
        await ctx.send(embed=embed)



    @commands.command(name="userinfo", aliases=["ui"], description="ユーザーの情報")
    async def userinfo(self, ctx, *, user: Union[discord.Member, discord.User,] = None):
        """`誰でも`"""

        def rv(content):
            if content == 'None': return 'なし'
            value = content.replace('online', 'オンライン').replace('offline', 'オフライン')
            value = value.replace("`create_instant_invite`", "`招待リンクを作成`").replace("`kick_members`",
                                                                                   "`メンバーをキック`").replace(
                "`ban_members`", "`メンバーをBan`")
            value = value.replace("`administrator`", "`管理者`").replace("`manage_channels`", "`チャンネルの管理`").replace(
                "`manage_guild`", "`サーバー管理`")
            value = value.replace("`add_reactions`", "`リアクションの追加`").replace("`view_audit_log`", "`サーバーログの表示`").replace(
                "`priority_speaker`", "`優先スピーカー`")
            value = value.replace("`stream`", "`配信`").replace("`read_messages`", "`メッセージを読む`").replace(
                "`send_messages`", "`メッセージを送信`")
            value = value.replace("`send_tts_messages`", "`TTSメッセージを送信`").replace("`manage_messages`",
                                                                                  "`メッセージの管理`").replace("`embed_links`",
                                                                                                        "`埋め込みリンク`")
            value = value.replace("`attach_files`", "`ファイルの添付`").replace("`read_message_history`",
                                                                         "`メッセージ履歴を読む`").replace("`mention_everyone`",
                                                                                                 "`全員宛メンション`")
            value = value.replace("`external_emojis`", "`外部の絵文字の使用`").replace("`view_guild_insights`",
                                                                              "`サーバーインサイトを見る`").replace("`connect`",
                                                                                                        "`接続`")
            value = value.replace("`speak`", "`発言`").replace("`mute_members`", "`発言`").replace("`mute_members`",
                                                                                               "`メンバーをミュート`").replace(
                "`deafen_members`", "`メンバーのスピーカーをミュート`")
            value = value.replace("`move_members`", "`メンバーの移動`").replace("`use_voice_activation`", "`音声検出を使用`").replace(
                "`change_nickname`", "`ニックネームの変更`")
            value = value.replace("`manage_nicknames`", "`ニックネームの管理`").replace("`manage_roles`", "`役職の管理`").replace(
                "`manage_webhooks`", "`webhookの管理`")
            value = value.replace("`manage_emojis`", "`絵文字の管理`")
            return value

        user = user or ctx.author
        e = discord.Embed(color=0xb300ff)
        roles = [r.mention for r in user.roles]
        e.set_author(name="ユーザー情報")

        since_created = (ctx.message.created_at - user.created_at).days
        since_joined = (ctx.message.created_at - user.joined_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        user_joined = user.joined_at.strftime("%d %b %Y %H:%M")

        created_at = f"{user_created}\n({since_created} days ago)"
        joined_at = f"{user_joined}\n({since_joined} days ago)"

        e.add_field(name="ユーザー名", value=f"{user}({user.id})", inline=True)

        voice = getattr(user, 'voice', None)
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
            e.add_field(name='Voice', value=voice, inline=True)
        else:
            e.add_field(name="voice", value="入っていません")



        if user.bot:
            e.add_field(name="Botですか",value="はい")
        else:
            e.add_field(name="Botですか", value="いいえ")

        e.add_field(name='Status', value=user.status)

        e.add_field(name="ニックネーム", value=user.display_name)

        if bool(user.premium_since):
            e.add_field(name="ブースト？", value="してます")
        else:
            e.add_field(name="ブースト", value="してない")

        e.add_field(name="Discord参加日:", value=created_at, inline=True)
        e.add_field(name="サーバー参加日", value=joined_at, inline=True)

        e.add_field(name="Highest Role:", value=user.top_role.mention)
        print(user.top_role.mention)

        if roles:
            e.add_field(name=f"Roles({len(roles)})",
                        value=', '.join(roles) if len(roles) < 40 else f'{len(roles)} roles', inline=False)

        e.add_field(name='Avatar Link', value=user.avatar_url, inline=False)
        if user.avatar:
            e.set_thumbnail(url=user.avatar_url)

        if isinstance(user, discord.User):
            e.set_footer(text='This member is not in this server.')

        pers = [f"`{c}`" for c in dict(user.guild_permissions) if dict(user.guild_permissions)[c] is True]
        e.add_field(name=f"権限({len(pers)})", value=rv(",".join(pers)))

        shared = sum(g.get_member(user.id) is not None for g in self.bot.guilds)
        e.add_field(name="共通鯖数",value=shared)

        await ctx.send(embed=e)

    @commands.command(aliases=["messagehis", "mhis"], description="指定した数のメッセージの履歴を表示するよ！")
    async def messagehistory(self,ctx, num: int):
        async for i in ctx.channel.history(limit=num):
            await ctx.send(f"{i.author.name}#{i.author.discriminator}: {i.content}")



    @commands.command()
    async def emojiinfo(self,ctx, *, emj: commands.EmojiConverter = None):

        if emj is None:
            await ctx.send("einfo-needarg")
        else:
            embed = discord.Embed(
                title=emj.name, description=f"id:{emj.id}")
            embed.add_field(name="einfo-animated", value=emj.animated)
            embed.add_field(name="einfo-manageout", value=emj.managed)
            if emj.user:
                embed.add_field(name="einfo-adduser",
                                value=str(emj.user))
            embed.add_field(name="url", value=emj.url)
            embed.set_footer(text="einfo-addday")
            embed.set_thumbnail(url=emj.url)
            embed.timestamp = emj.created_at
            await ctx.send(embed=embed)

    @commands.command(name="user")
    async def user(self, ctx, *, user: Union[discord.Member, discord.User] = None):
        """Shows info about a user."""

        user = user or ctx.author
        e = discord.Embed(title="外部ユーザー情報", color=0x0066ff)
        roles = [role.name.replace('@', '@\u200b') for role in getattr(user, 'roles', [])]
        e.set_author(name=str(user))
        since_created = (ctx.message.created_at - user.created_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        created_at = f"{user_created}\n({since_created} days ago)"
        e.add_field(name='ユーザー名', value=f"{user.name}({user.id})", inline=False)
        e.add_field(name="Discord参加日:", value=created_at, inline=True)

        voice = getattr(user, 'voice', None)
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
            e.add_field(name='Voice', value=voice, inline=False)

        if roles:
            e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles',
                        inline=False)
        if user.avatar:
            e.set_thumbnail(url=user.avatar_url)

        if user.bot:
            e.add_field(name="Botですか",value="はい")
        else:
            e.add_field(name="Botですか", value="いいえ")

        if isinstance(user, discord.User):
            e.set_footer(text='This member is not in this server.')

        await ctx.send(embed=e)

    @commands.command(name="roleinfo", aliases=["ri", "role"], description="```役職の情報```")
    async def roleinfo(self, ctx, *, role: commands.RoleConverter = None):
        """`誰でも`"""
        if role is None:
            await ctx.send(ctx._("roleinfo-howto"))
        elif role.guild == ctx.guild:
            embed = discord.Embed(title=role.name, description=f"id:{role.id}", color=0x5d00ff)
            if role.hoist:
                embed.add_field(name="別表示", value="はい")
            else:
                embed.add_field(name="別表示", value="いいえ")
            if role.mentionable:
               embed.add_field(name="メンション可能", value="はい")
            else:
                embed.add_field(name="メンション可能",value='いいえ')

            embed.add_field(name='メンバー数', value=str(len(role.members)))
            embed.add_field(name='カラーコード', value=str(role.color))

            embed.add_field(name='作成日時', value=role.created_at.__format__('%x at %X'))
            embed.add_field(name='メンバー [%s]' % len(role.members),
                            value='%s Online' % sum(1 for m in role.members if m.status != discord.Status.offline),
                            inline=True)

            perms = ""
        if role.permissions.administrator:
            perms += "管理者権限, "
        if role.permissions.create_instant_invite:
            perms += "招待リンクの作成, "
        if role.permissions.kick_members:
            perms += "Kick権限, "
        if role.permissions.ban_members:
            perms += "Ban権限, "
        if role.permissions.manage_channels:
            perms += "チャンネルの管理, "
        if role.permissions.manage_guild:
            perms += "サーバーの管理, "
        if role.permissions.add_reactions:
             perms += "リアクションの追加, "
        if role.permissions.view_audit_log:
            perms += "サーバーの統計を表示, "
        if role.permissions.read_messages:
            perms += "メッセージの表示, "
        if role.permissions.send_messages:
            perms += "メッセージを送信, "
        if role.permissions.send_tts_messages:
            perms += "TTSメッセージの送信, "
        if role.permissions.manage_messages:
            perms += "メッセージを管理, "
        if role.permissions.embed_links:
            perms += "埋め込みリンクの送信, "
        if role.permissions.attach_files:
            perms += "ファイルの添付, "
        if role.permissions.read_message_history:
            perms += "メッセージの履歴の表示, "
        if role.permissions.mention_everyone:
            perms += "役職,全員宛メンション, "
        if role.permissions.external_emojis:
            perms += "外侮の絵文字を使用, "
        if role.permissions.connect:
            perms += "接続, "
        if role.permissions.speak:
            perms += "発言, "
        if role.permissions.mute_members:
            perms += "メンバーをミュート, "
        if role.permissions.deafen_members:
            perms += "スピーカーミュート, "
        if role.permissions.move_members:
            perms += "メンバーの移動, "
        if role.permissions.use_voice_activation:
            perms += "音声検出を使用, "
        if role.permissions.change_nickname:
            perms += "ニックネームを変える, "
        if role.permissions.manage_nicknames:
            perms += "ニックネームを管理, "
        if role.permissions.manage_roles:
            perms += "役職を管理, "
        if role.permissions.manage_webhooks:
            perms += "webhookを管理, "
        if role.permissions.manage_emojis:
            perms += "絵文字を管理, "

        if perms is None:
            perms = "None"
        else:
            perms = perms.strip(", ")

            embed.add_field(name='Permissions', value=f"`{perms}`")

            hasmember = ""
            for m in role.members:
                hasmember = hasmember + f"{m.mention},"
            if not hasmember == "":
                if len(hasmember) <= 1024:
                    embed.add_field(name="メンバー", value=hasmember)
                else:
                    embed.add_field(name="メンバー", value="ユーザーが多すぎます")
            else:
                embed.add_field(name="メンバー", value="None")

            await ctx.send(embed=embed)

    @commands.command(name="avatar", description="```ユーザーのアイコン```")
    async def avatar(self, ctx, *, user: Union[discord.Member, discord.User] = None):
        """`誰でも`"""
        embed = discord.Embed(color=0x5d00ff)
        user = user or ctx.author
        avatar = user.avatar_url_as(static_format='png')
        embed.set_author(name=str(user), url=avatar)
        embed.set_image(url=avatar)
        await ctx.send(embed=embed)

    @commands.command(aliases=['e'])
    async def emoji(self, ctx, emojiname: str):
        """`誰でも`"""
        emoji = discord.utils.find(lambda e: e.name.lower() == emojiname.lower(), self.bot.emojis)
        if emoji:
            tempEmojiFile = 'tempEmoji.png'
            async with aiohttp.ClientSession() as cs:
                async with cs.get(str(emoji.url)) as img:
                    with open(tempEmojiFile, 'wb') as f:
                        f.write(await img.read())
                f = discord.File(tempEmojiFile)
                await ctx.send(file=f)
                os.remove(tempEmojiFile)
        else:
            await ctx.send(':x: Konnte das angegebene Emoji leider nicht finden :(')

    @commands.command(aliases=['emotes'])
    async def emojis(self, ctx):
        """`誰でも`"""
        msg = ''
        for emoji in self.bot.emojis:
            if len(msg) + len(str(emoji)) > 1000:
                await ctx.send(msg)
                msg = ''
            msg += str(emoji)
        await ctx.send(msg)

    @commands.command(name="messageinfo", aliases=["msg", "message"], description="```メッセージの情報```")
    async def messageinfo(self, ctx, target: Union[commands.MessageConverter, None]):
        """`誰でも`"""
        if target:
            fetch_from = "引数"
            msg = target
        else:
            if ctx.message.reference and ctx.message.type == discord.MessageType.default:
                if ctx.message.reference.cached_message:
                    fetch_from = "返信"
                    msg = ctx.message.reference.cached_message
                else:
                    try:
                        fetch_from = "返信"
                        msg = await self.bot.get_channel(ctx.message.reference.channel_id).fetch_message(
                            ctx.message.reference.message_id)
                    except:
                        fetch_from = "コマンド実行メッセージ"
                        msg = ctx.message

            else:
                fetch_from = "コマンド実行メッセージ"
                msg = ctx.message

        e = discord.Embed(title=f"メッセージ{fetch_from}", descriptio=msg.system_content, color=0x5d00ff)
        e.set_author(name=f"{msg.author.display_name}({msg.author.id}){'[bot]' if msg.author.bot else ''}のメッセージ",
                     icon_url=msg.author.avatar_url_as(static_format="png"))

        post_time = msg.created_at.strftime("%d/%m/%Y %H:%M:%S")

        if msg.edited_at:
            edit_time = msg.edited_at.strftime("%d/%m/%Y %H:%M:%S")

        else:
            edit_time = "なし"

        e.set_footer(text=f"メッセージ送信時間:{post_time}/最終編集時間:{edit_time}")

        e.add_field(name="メッセージ", value=str(msg.id))
        e.add_field(name="システムメッセージ？", value=msg.is_system())
        e.add_field(name="添付ファイル数", value=f"{len(msg.attachments)}個")
        e.add_field(name="埋め込み数", value=f"{len(msg.embeds)}個")

        if msg.guild.rules_channel and msg.channel_id == msg.guild.rules_channel.id:
            chtype = f"{msg.channel.name}({msg.channel.id}):ルールチャンネル"
        elif msg.channel.is_news():
            chtype = f"{msg.Channel.name}({msg.channel.id}):アナウンスチャンネル"
        else:
            chtype = f"{msg.channel.name}({msg.channel.id}):テキストチャンネル"
        e.add_field(name="メッセージの送信チャンネル", value=chtype)

        if msg.reference:
            e.add_field(name="メッセージの返信等", value=f"返信元確認用:`{msg.reference.channel_id}-{msg.reference.message_id}`")

        e.add_field(name="メンションの内訳",
                    value=f"全員宛メンション:{msg.mention_everyone}\nユーザーメンション:{len(msg.mentions)}個\n役職メンション:{len(msg.role_mentions)}個\nチャンネルメンション:{len(msg.channel_mentions)}個")
        if msg.webhook_id:
            e.add_field(name="webhook投稿", value=f"ID:{msg.webhook_id}")
        e.add_field(name="ピン留めされてるかどうか", value=str(msg.pinned))
        if len(msg.reactions) != 0:
            e.add_field(name="リアクション", value=",".join({f"{r.emoji}:{r.count}" for r in msg.reactions}))

        e.add_field(name="メッセージフラグ", value=[i[0] for i in iter(msg.flags) if i[1]])

        e.add_field(name="メッセージに飛ぶ", value=msg.jump_url)

        try:
            await ctx.replay(embed=e, mentions_author=False)
        except:
            await ctx.send(embed=e)

    @commands.command(name="channelinfo", aliases=["chinfo"], description="```チャンネルの情報```")
    async def channelinfo(self, ctx, target=None):
        """`誰でも`"""
        if target is None:
            target = ctx.channel
        else:
            try:
                target = await commands.TextChannelConverter().convert(ctx, target)
            except:
                try:
                    target = await commands.VoiceChannelConverter().convert(ctx, target)
                except:
                    try:
                        target = await commands.CategoryChannelConverter().convert(ctx, target)
                    except:
                        try:
                            target = self.bot.get_channel(int(target))
                        except:
                            await ctx.send("引数をチャンネルに変換できませんでした。")
                            return

        if target is None:
            return await ctx.send("そのチャンネルが見つかりませんでした。")
        if not target.guild.id == ctx.guild.id:
            await ctx.send("別のサーバーのチャンネルです")
            return
        if isinstance(target, discord.TextChannel):
            if target.is_news():
                if "NEWS" in target.guild.features:
                    e = discord.Embed(name="チャンネル情報", description=f"{target.name}(タイプ:アナウンス)\nID:{target.id}",
                                      color=0x00ff00)
                else:
                    e = discord.Embed(name="チャンネル情報", description=f"{target.name}(タイプ:アナウンス(フォロー不可))\nID:{target.id}")
            else:
                e = discord.Embed(name="チャンネル情報", description=f"{target.name}(タイプ:テキスト)\nID:{target.id}", color=0x5d00ff)
            e.timestamp = target.created_at
            if target.category:
                e.add_field(name="所属するカテゴリ", value=f"{target.category.name}({target.category.id})")
            e.add_field(name="チャンネルトピック", value=target.topic or "なし")
            if not target.slowmode_delay == 0:
                e.add_field(name="スローモードの時間", value=f"{target.slowmode_delay}秒")
            e.add_field(name="NSFW指定有無", value=target.is_nsfw())

            mbs = ""
            for m in target.members:
                if len(mbs + f"`{m.name}`,") >= 1020:
                    mbs = mbs + f"他"
                    break
                else:
                    mbs = mbs + f"`{m.name}`,"
            if mbs != "":
                e.add_field(name=f"メンバー({len(target.members)}人)", value=mbs, inline=False)
            await ctx.send(embed=e)
        elif isinstance(target, discord.VoiceChannel):
            e = discord.Embed(name="チャンネル情報", description=f"{target.name}(タイプ:ボイス)\nID:{target.id}")
            e.timestamp = target.created_at
            if target.category:
                e.add_field(name="所属するカテゴリ", value=f"{target.category.name}({target.category.id})")
            e.add_field(name="チャンネルビットレート", value=f"{target.bitrate / 1000}Kbps")
            if not target.user_limit == 0:
                e.add_field(name="ユーザー数制限", value=f"{target.user_limit}人")
            mbs = ""
            for m in target.members:
                if len(mbs + f"`{m.name}`,") >= 1020:
                    mbs = mbs + f"他"
                    break
                else:
                    mbs = mbs + f"`{m.name}`,"
            if mbs != "":
                e.add_field(name=f"参加可能なメンバー({len(target.members)}人)", value=mbs, inline=False)
            await ctx.send(embed=e)
        elif isinstance(target, discord.CategoryChannel):
            e = discord.Embed(name="チャンネル情報", description=f"{target.name}(タイプ:カテゴリ)\nID:{target.id}")
            e.timestamp = target.created_at
            e.add_field(name="NSFW指定有無", value=target.is_nsfw())
            mbs = ""
            for c in target.channels:
                if c.type is discord.ChannelType.news:
                    if "NEWS" in target.guild.features:
                        chtype = "アナウン素"
                    else:
                        chtype = "アナウンス(フォロー不可)"
                elif c.type is discord.ChannelType.store:
                    chtype = "ストア"
                elif c.type is discord.ChannelType.voice:
                    chtype = "ボイス"
                elif c.type is discord.ChannelType.text:
                    chtype = "テキスト"
                else:
                    chtype = str(c.type)
                if len(mbs + f"`{c.name}({chtype})`,") >= 1020:
                    mbs = mbs + f"他"
                    break
                else:
                    mbs = mbs + f"`{c.name}({chtype})`,"
            if mbs != "":
                e.add_field(name=f"所属するチャンネル({len(target.channels)}チャンネル)", value=mbs, inline=False)
            await ctx.send(embed=e)



def setup(bot):
    bot.add_cog(infoCog(bot))