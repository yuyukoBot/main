
import aiohttp
import datetime
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
from typing import Union
import time, struct,subprocess
import asyncio
from discord_components import DiscordComponents,Button,ButtonStyle,InteractionType, Select, SelectOption
import platform
from discord.ext import commands
from platform import python_version
from discord import __version__ as discord_version

from collections import OrderedDict, deque, Counter
import datetime
import time
import os
import random

import discord

import psutil


class information(commands.Cog):

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

    @commands.command(name="omikuji")
    async def omikuji(self, ctx):

        omikuzi = [
            "大吉だよ！\nおめでとう" if i < 2 else
            "中吉" if 2 <= i < 10 else
            "小吉" if 10 <= i < 20 else
            "吉" if 20 <= i < 40 else
            "末吉" if 40 <= i < 50 else
            "凶" if 50 <= i < 55 else
            "中凶" if 55 <= i < 59 else
            "大凶" for i in range(61)]
        e = discord.Embed(title="おみくじ～")

        msg = await ctx.send(embed=e)
        async with ctx.typing():
            e = discord.Embed(title="おみくじ~",description="がらがら～～")
            await asyncio.sleep(2)
        await msg.edit(content=None, embed=e)

        async with ctx.typing():
            e = discord.Embed(title="おみくじ")
            e.add_field(name="結果！", value=omikuzi[random.randrange(len(omikuzi))])
            await asyncio.sleep(2)
        await msg.edit(content=None, embed=e)

    @commands.command(name='infos')
    async def select_test(self, ctx, *, user: Union[discord.Member, discord.User,] = None):
        await ctx.send("We are testing selects!",
                       components=
                       [Select(placeholder="Choose what you want to see!",
                               options=[
                                   SelectOption(
                                       label="基本的な情報",
                                       value="option1",
                                       description="See option 1",
                                       emoji="😄"
                                       # you can use discord.Parti ... emoji to use a custom one (i dont know what its called)
                                   ),
                                   SelectOption(
                                       label="ステータス等",
                                       value="option2",
                                       description="See option 2",
                                       emoji="😄"
                                       # you can use discord.Parti ... emoji to use a custom one (i dont know what its called)
                                   ),
                                   SelectOption(
                                       label="役職",
                                       value="option3",
                                       description="See option 3",
                                       emoji="😄"
                                       # you can use discord.Parti ... emoji to use a custom one (i dont know what its called)
                                   ),
                                   SelectOption(
                                       label="権限",
                                       value="option4",
                                       description="See option 4",
                                       emoji="😄"
                                       # you can use discord.Parti ... emoji to use a custom one (i dont know what its called)
                                   ),
                               ])]
                       )
        e1 = discord.Embed(title="ui", description="下記参照")
        e2 = discord.Embed(title="embed2", description="a really exciting embed")
        e3 = discord.Embed(title="embed3", description="a really exciting embed")
        e4 = discord.Embed(title="embede")
        user = user or ctx.author

        badges = {
            "staff": "<:staff:836951948745900063>",
            "partner": "<:partner:836950588536127508>",
            "hypesquad": "<:hypesquadevents:724328584789098639>",
            "hypesquad_balance": "<:balance:855966162483281940>",
            "hypesquad_bravery": "<:bravery:855966487956684821>",
            "hypesquad_brilliance":
                "<:brilince:855966748250341396>",
            "premium_since": "test",
            "bug_hunter": "<:bughunt:724588087052861531>",
            "bug_hunter_level_2": "<:bug2:699986097694048327>",
            "verified_bot_developer": "<:verifed:836952740818976770>",
            "early_supporter": "<:earlysupporter:724588086646014034>",

        }
        flags = [
            flag for flag, value in dict(user.public_flags).items() if
            value is True
        ]
        flagstr = ""
        for badge in badges.keys():
            if badge in flags:
                flagstr += f" {badges[badge]} "
        n = False

        roles = [r.mention for r in user.roles]


        while True:
            try:  # try except is not required but i would recommend using it
                event = await self.bot.wait_for("select_option", check=None)

                label = event.component[0].label

                if label == "基本的な情報":
                    msg = await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=True,  # we dont want to spam someone
                        embed=e1
                    )
                    since_created = (ctx.message.created_at - user.created_at).days
                    since_joined = (ctx.message.created_at - user.joined_at).days
                    user_created = user.created_at.strftime("%d %b %Y %H:%M")
                    user_joined = user.joined_at.strftime("%d %b %Y %H:%M")

                    created_at = f"{user_created}\n({since_created} days ago)"
                    joined_at = f"{user_joined}\n({since_joined} days ago)"
                    e = discord.Embed(title="ユーザー情報",description=f"{user}({user.id})")
                    e.add_field(name="Discord参加日:", value=created_at, inline=True)
                    e.add_field(name="サーバー参加日", value=joined_at, inline=True)
                    e.add_field(name="ニックネーム",value=user.display_name)
                    if user.bot:
                        e.add_field(name="Botですか", value="はい")
                    else:
                        e.add_field(name="Botですか", value="いいえ")

                    if user.avatar:
                        e.set_thumbnail(url=user.avatar_url)
                    await ctx.send(embed=e)


                elif label == "ステータス等":
                    await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=True,  # we dont want to spam someone
                        embed=e2
                    )
                    if n:
                        flagstr += f" <:nitro:724328585418113134>"
                    e = discord.Embed(title="ステータス等",description=f'{user}({user.id}{flagstr})')

                    if len(flagstr) != 0:
                        e.add_field(name="Badges", value=flagstr)

                    if str(user.status) == "online":
                        e.add_field(name="ステータス", value='<:online:855965213156311091>  ')
                    elif str(user.status) == "offline":
                        e.add_field(name="ステータス", value='<:offline:855965198221180968>')
                    elif str(user.status) == "idle":
                        e.add_field(name="ステータス", value='<:afk:855965231740878878>')
                    elif str(user.status) == "dnd":
                        e.add_field(name="ステータス", value='<:dnd:855965222640156682> ')

                    if user.avatar:
                        e.set_thumbnail(url=user.avatar_url)

                    if user.mobile_status:
                        e.add_field(name="使用デバイス(モバイル)", value=':mobile_phone:')
                    elif user.desktop_status:
                        e.add_field(name="使用デバイス(デスクトップ)", value=':desktop:')

                    elif user.web_status:
                        e.add_field(name="使用デバイス(web)", value=':computer:')

                    if user.activity is not None:
                        try:
                            if user.activity.type == discord.ActivityType.custom:
                                e.add_field(name="プレイ中", value=user.activity)
                            else:
                                e.add_field(name="プレイ中", value=f'{user.activity.name}')
                        except:
                            e.add_field(name="プレイ中", value=user.activity)

                    if bool(user.premium_since):
                        e.add_field(name="ブースト？", value="してます")
                    else:
                        e.add_field(name="ブースト", value="してない")

                    await ctx.send(embed=e)
                elif label == "役職":
                    await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=False,  # we dont want to spam
                        embed=e3
                    )
                    e = discord.Embed(title="ユーザー情報",description=f'{user}({user.id})')
                    e.add_field(name="Highest Role:", value=user.top_role.mention)
                    print(user.top_role.mention)

                    if roles:
                        e.add_field(name=f"Roles({len(roles)})",
                                    value=', '.join(roles) if len(roles) < 40 else f'{len(roles)} roles', inline=False)

                    if user.avatar:
                        e.set_thumbnail(url=user.avatar_url)
                    await ctx.send(embed=e)

                elif label == "権限":
                    await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=False,  # we dont want to spam
                        embed=e4
                    )
                    user_permission = user.guild_permissions

                    server_permission = {
                        'administrator': '管理者', 'read_messages': 'チャンネルを見る', 'manage_channels': 'チャンネルの管理',
                        'manage_roles': 'ロールの管理', 'manage_emojis': '絵文字の管理',
                        'view_audit_log': 'サーバーログの表示', 'view_guild_insights': 'サーバーインサイトを見る',
                        'manage_webhooks': 'webhookの管理', 'manage_guild': 'サーバー管理'
                    }
                    member_permission = {
                        'create_instant_invite': '招待リンクを作成', 'change_nickname': 'ニックネームの変更',
                        'manage_nicknames': 'ニックネームの管理', 'kick_members': 'メンバーをキック',
                        'ban_members': 'メンバーをBAN'
                    }
                    ch_permission = {
                        'send_messages': 'メッセージを送信', 'embed_links': '埋め込みリンク', 'attach_files': 'ファイルを添付',
                        'add_reactions': 'リアクションの追加', 'external_emojis': '外部の絵文字の利用',
                        'mention_everyone': '@everyone、@here、全てのロールにメンション', 'manage_messages': 'メッセージの管理',
                        'read_message_history': 'メッセージ履歴を読む', 'send_tts_messages': 'テキスト読み上げメッセージを送信する',
                        'use_slash_commands': 'スラッシュコマンドを使用'
                    }
                    voice_permission = {
                        'connect': '接続', 'speak': '発言', 'stream': '動画',
                        'use_voice_activation': '音声検出を使用', 'priority_speaker': '優先スピーカー',
                        'mute_members': 'メンバーをミュート', 'deafen_members': 'メンバーのスピーカーをミュート',
                        'move_members': 'メンバーを移動', 'request_to_speak': 'スピーカー参加をリクエスト'
                    }

                    s_perm_text = ''
                    m_perm_text = ''
                    c_perm_text = ''
                    not_vperm_text = ''
                    not_cperm_text = ''
                    not_mperm_text = ''
                    not_sperm_text = ''
                    v_perm_text = ''
                    user_permission_list = []
                    for rp in list(user_permission):
                        if rp[1]:
                            user_permission_list.append(rp[0])

                    for sp in list(server_permission):
                        if sp in user_permission_list:
                            s_perm_text += f"✅:{server_permission[sp]}"
                        else:
                            not_sperm_text += f"❌:{server_permission[sp]}"
                    for sp in list(member_permission):
                        if sp in user_permission_list:
                            m_perm_text += f"✅:{member_permission[sp]}"
                        else:
                            not_mperm_text += f"❌:{member_permission[sp]}"
                    for sp in list(ch_permission):
                        if sp in user_permission_list:
                            c_perm_text += f"✅:{ch_permission[sp]}"
                        else:
                            not_cperm_text += f"❌:{ch_permission[sp]}"
                    for sp in list(voice_permission):
                        if sp in user_permission_list:
                            v_perm_text += f"✅:{voice_permission[sp]}"
                        else:
                            not_vperm_text += f"❌:{voice_permission[sp]}"
                    e = discord.Embed(title="ユーザー情報",description=f'{user}({user.id})',color=self.bot.color)
                    e.add_field(name='サーバー全般', value=f'`{s_perm_text}`,`{not_sperm_text}`')
                    e.add_field(name='メンバー', value=f'`{m_perm_text}`,`{not_mperm_text}`')
                    e.add_field(name='テキストチャンネル', value=f'`{c_perm_text}`,`{not_cperm_text}`')
                    e.add_field(name='ボイス', value=f'`{v_perm_text}`,`{not_vperm_text}`')
                    if user.avatar:
                        e.set_thumbnail(url=user.avatar_url)
                    await ctx.send(embed=e)


            except discord.NotFound:
                print(
                    "error.")  # since this is bugged, we cant send an error. this error raises every time you use a select, but if this is fixed you can send what ever you want.

    @commands.command()
    async def requests(self, ctx, command, info):
        e = discord.Embed(title="要望", description=f"リクエストした人\n{ctx.author}")
        e.add_field(name="コマンド名", value=command)
        e.add_field(name="内容", value=info)
        await ctx.send(embed=e)

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

        rlist = "@".join([i.name for i in guild.roles])
        if len(rlist) <= 1000:
            e.add_field(name="役職", value=rlist)



        emojis = self._getEmojis(guild.emojis)

        e.add_field(name='カスタム絵文字', value=emojis, inline=False)



        e.add_field(name="features",
                    value=f"```{','.join(guild.features)}```")


        await ctx.send(embed=e)



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
                    value=f'{("<:categorie:798883839124308008>")}:{len(guild.categories)}\n{(":speech_balloon:")}:{len(guild.text_channels)}\n{(":mega:")}:{len(guild.voice_channels)}\n{(":pager:")}:{len(guild.stage_channels)}')

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
        conn = sqlite3.connect('main.sqlite')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM ServerSetting WHERE guild_id = ?', (guild.id,))
        data = cursor.fetchall()
        settings = data[0]
        if not data:
            return
        e.add_field(name='ログチャンネル', value=self.bot.get_channel(int(settings[4])).mention if settings[4] else 'なし')
        e.add_field(name='Welcomeチャンネル',value=self.bot.get_channel(int(settings[1])).mention if settings[1] else 'なし')


        roles = self._getRoles(guild.roles)
        if len(roles) <= 1024:
            e.add_field(name="役職", value=roles, inline=False)
        else:
            e.add_field(name="役職", value="多いですよ")

        rlist = ",".join([i.name for i in guild.roles])
        if len(rlist) <= 1000:
            e.add_field(name=ctx._("serverinfo-roles"), value=rlist)

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

        user = user or ctx.author
        e = discord.Embed(color=0xb300ff)
        roles = [r.mention for r in user.roles]


        e.set_author(name="ユーザー情報")
        badges = {
            "staff": "<:staff:836951948745900063>",
            "partner": "<:partner:836950588536127508>",
            "hypesquad": "<:hypesquadevents:724328584789098639>",
            "hypesquad_balance": "<:balance:855966162483281940>",
            "hypesquad_bravery": "<:bravery:855966487956684821>",
            "hypesquad_brilliance":
            "<:brilince:855966748250341396>",
            "premium_since": "test",
            "bug_hunter": "<:bughunt:724588087052861531>",
            "bug_hunter_level_2": "<:bug2:699986097694048327>",
            "verified_bot_developer": "<:verifed:836952740818976770>",
            "early_supporter": "<:earlysupporter:724588086646014034>",

        }
        flags = [
            flag for flag, value in dict(user.public_flags).items() if
            value is True
                 ]
        flagstr = ""
        for badge in badges.keys():
            if badge in flags:
                flagstr += f" {badges[badge]} "
        n = False
        if n:
            flagstr += f" <:nitro:724328585418113134>"
        if len(flagstr) != 0:
            e.add_field(name="Badges", value=flagstr)
        since_created = (ctx.message.created_at - user.created_at).days
        since_joined = (ctx.message.created_at - user.joined_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        user_joined = user.joined_at.strftime("%d %b %Y %H:%M")

        created_at = f"{user_created}\n({since_created} days ago)"
        joined_at = f"{user_joined}\n({since_joined} days ago)"

        e.add_field(name="ユーザー名", value=f"{user}({user.id})", inline=True)
        if user.id in [478126443168006164, 602680118519005184, 691300045454180383]:#admin
            e.add_field(name="権限",value="admin")
        else:
            e.add_field(name="権限",value="一般")

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





        e.add_field(name="ニックネーム", value=user.display_name)
        if str(user.status) == "online":
            e.add_field(name="ステータス",value='<:online:855965213156311091>  ')
        elif str(user.status) == "offline":
            e.add_field(name="ステータス",value='<:offline:855965198221180968>')
        elif str(user.status) == "idle":
            e.add_field(name="ステータス",value='<:afk:855965231740878878>')
        elif str(user.status) == "dnd":
            e.add_field(name="ステータス",value='<:dnd:855965222640156682> ')

        if user.mobile_status:
            e.add_field(name="使用デバイス(モバイル)",value=':mobile_phone:')
        elif user.desktop_status:
            e.add_field(name="使用デバイス(デスクトップ)",value=':desktop:')

        elif user.web_status:
            e.add_field(name="使用デバイス(web)",value=':computer:')

        if user.activity is not None:
            try:
                if user.activity.type == discord.ActivityType.custom:
                    e.add_field(name="プレイ中", value=user.activity)
                else:
                    e.add_field(name="プレイ中", value=f'{user.activity.name}')
            except:
                e.add_field(name="プレイ中",value=user.activity)

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

        user_permission = user.guild_permissions



        server_permission = {
            'administrator': '管理者', 'read_messages': 'チャンネルを見る', 'manage_channels': 'チャンネルの管理',
            'manage_roles': 'ロールの管理', 'manage_emojis': '絵文字の管理',
            'view_audit_log': 'サーバーログの表示', 'view_guild_insights': 'サーバーインサイトを見る',
            'manage_webhooks': 'webhookの管理', 'manage_guild': 'サーバー管理'
        }
        member_permission = {
            'create_instant_invite': '招待リンクを作成', 'change_nickname': 'ニックネームの変更',
            'manage_nicknames': 'ニックネームの管理', 'kick_members': 'メンバーをキック',
            'ban_members': 'メンバーをBAN'
        }
        ch_permission = {
            'send_messages': 'メッセージを送信', 'embed_links': '埋め込みリンク', 'attach_files': 'ファイルを添付',
            'add_reactions': 'リアクションの追加', 'external_emojis': '外部の絵文字の利用',
            'mention_everyone': '@everyone、@here、全てのロールにメンション', 'manage_messages': 'メッセージの管理',
            'read_message_history': 'メッセージ履歴を読む', 'send_tts_messages': 'テキスト読み上げメッセージを送信する',
            'use_slash_commands': 'スラッシュコマンドを使用'
        }
        voice_permission = {
            'connect': '接続', 'speak': '発言', 'stream': '動画',
            'use_voice_activation': '音声検出を使用', 'priority_speaker': '優先スピーカー',
            'mute_members': 'メンバーをミュート', 'deafen_members': 'メンバーのスピーカーをミュート',
            'move_members': 'メンバーを移動', 'request_to_speak': 'スピーカー参加をリクエスト'
        }

        s_perm_text = ''
        m_perm_text = ''
        c_perm_text = ''
        not_vperm_text = ''
        not_cperm_text = ''
        not_mperm_text = ''
        not_sperm_text = ''
        v_perm_text = ''
        user_permission_list = []
        for rp in list(user_permission):
            if rp[1]:
                user_permission_list.append(rp[0])

        for sp in list(server_permission):
            if sp in user_permission_list:
                s_perm_text += f"✅:{server_permission[sp]}"
            else:
                not_sperm_text += f"❌:{server_permission[sp]}"
        for sp in list(member_permission):
            if sp in user_permission_list:
                m_perm_text += f"✅:{member_permission[sp]}"
            else:
                not_mperm_text += f"❌:{member_permission[sp]}"
        for sp in list(ch_permission):
            if sp in user_permission_list:
                c_perm_text += f"✅:{ch_permission[sp]}"
            else:
                not_cperm_text += f"❌:{ch_permission[sp]}"
        for sp in list(voice_permission):
            if sp in user_permission_list:
                v_perm_text += f"✅:{voice_permission[sp]}"
            else:
                not_vperm_text += f"❌:{voice_permission[sp]}"

        e = discord.Embed()

        e.add_field(name='サーバー全般', value=f'`{s_perm_text}`,`{not_sperm_text}`')
        e.add_field(name='メンバー', value=f'`{m_perm_text}`,`{not_mperm_text}`')
        e.add_field(name='テキストチャンネル', value=f'`{c_perm_text}`,`{not_cperm_text}`')
        e.add_field(name='ボイス', value=f'`{v_perm_text}`,`{not_vperm_text}`')



        shared = sum(g.get_member(user.id) is not None for g in self.bot.guilds)
        e.add_field(name="共通鯖数",value=shared)

        await ctx.send(embed=e)

    @commands.command(aliases=["messagehis", "mhis"], description="指定した数のメッセージの履歴を表示するよ！")
    async def messagehistory(self,ctx, num: int):
        async for i in ctx.channel.history(limit=num):
            await ctx.send(f"{i.author.name}#{i.author.discriminator}: {i.content}")

    @commands.command()
    async def tutorial(self, ctx):
        em1 = discord.Embed(
            description=f"Hey there {ctx.author.mention}! It looks like you need some help moving around the bot! Let me help you!",
            color=0x36393f)
        em2 = discord.Embed(
            description=f"First, put in the command `{ctx.prefix}help`, this is where you can find all the commands!",
            color=0x36393f)
        em3 = discord.Embed(
            description=f"Awesome! Now, lets start you up with an profile! Execute the command `{ctx.prefix}start` to get make a profile!",
            color=0x36393f)
        em4 = discord.Embed(
            description=f"Great! Lets view your profile that you created. Execute the command `{ctx.prefix}profile` to view it!",
            color=0x36393f)
        em5 = discord.Embed(
            description=f"With `{ctx.prefix}profile`, you can view your **case points**. Those determine what rank you are and how hard the cases will be.\nNow, let move onto money. Use the command `{ctx.prefix}wallet` to view your coins.",
            color=0x36393f)
        em6 = discord.Embed(
            description=f"You can buy things with your coins. You earn coins by completing cases. Whenever you are ready, use the command `{ctx.prefix}case`. That's all! Have a great time and thank you for using The Detective!",
            color=0x36393f)
        await ctx.send(embed=em1)
        await asyncio.sleep(3)
        await ctx.send(embed=em2)
        msg = await self.bot.wait_for('message', check=lambda
            message: message.author == ctx.author and message.channel == ctx.channel)
        if msg.content.lower() == f"{ctx.prefix}help":
            await asyncio.sleep(0.5)
            await ctx.send(embed=em3)
            msg = await self.bot.wait_for('message', check=lambda
                message: message.author == ctx.author and message.channel == ctx.channel)
            if msg.content.lower() == f"{ctx.prefix}start":
                await asyncio.sleep(0.5)
                await ctx.send(embed=em4)
                msg = await self.bot.wait_for('message', check=lambda
                    message: message.author == ctx.author and message.channel == ctx.channel)
                if msg.content.lower() == f"{ctx.prefix}profile":
                    await asyncio.sleep(0.5)
                    await ctx.send(embed=em5)
                    msg = await self.bot.wait_for('message', check=lambda
                        message: message.author == ctx.author and message.channel == ctx.channel)
                    if msg.content.lower() == f"{ctx.prefix}wallet":
                        await asyncio.sleep(0.5)
                        await ctx.send(embed=em6)

    @commands.command(name="emojiinfo",description="絵文字の情報")
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

    @commands.command(name="user",description="外部ユーザーの情報")
    async def user(self, ctx, *, user: Union[discord.Member, discord.User] = None):
        """`誰でも`"""

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

    @commands.command(name="roleinfo", aliases=["ri", "role"], description="役職の情報")
    async def roleinfo(self, ctx, *, role: commands.RoleConverter = None):
        """`誰でも`"""

        if role is None:
            await ctx.send("役職が見つかりません")
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

            role_permission = role.permissions

            server_permission = {
                'administrator': '管理者', 'read_messages': 'チャンネルを見る', 'manage_channels': 'チャンネルの管理',
                'manage_roles': 'ロールの管理', 'manage_emojis': '絵文字の管理',
                'view_audit_log': 'サーバーログの表示', 'view_guild_insights': 'サーバーインサイトを見る',
                'manage_webhooks': 'webhookの管理', 'manage_guild': 'サーバー管理'
            }
            member_permission = {
                'create_instant_invite': '招待リンクを作成', 'change_nickname': 'ニックネームの変更',
                'manage_nicknames': 'ニックネームの管理', 'kick_members': 'メンバーをキック',
                'ban_members': 'メンバーをBAN'
            }
            ch_permission = {
                'send_messages': 'メッセージを送信', 'embed_links': '埋め込みリンク', 'attach_files': 'ファイルを添付',
                'add_reactions': 'リアクションの追加', 'external_emojis': '外部の絵文字の利用',
                'mention_everyone': '@everyone、@here、全てのロールにメンション', 'manage_messages': 'メッセージの管理',
                'read_message_history': 'メッセージ履歴を読む', 'send_tts_messages': 'テキスト読み上げメッセージを送信する',
                'use_slash_commands': 'スラッシュコマンドを使用'
            }
            voice_permission = {
                'connect': '接続', 'speak': '発言', 'stream': '動画',
                'use_voice_activation': '音声検出を使用', 'priority_speaker': '優先スピーカー',
                'mute_members': 'メンバーをミュート', 'deafen_members': 'メンバーのスピーカーをミュート',
                'move_members': 'メンバーを移動', 'request_to_speak': 'スピーカー参加をリクエスト'
            }

            s_perm_text = ''
            m_perm_text = ''
            c_perm_text = ''
            not_vperm_text = ''
            not_cperm_text = ''
            not_mperm_text = ''
            not_sperm_text = ''
            v_perm_text = ''
            user_permission_list = []
            for rp in list(role_permission):
                if rp[1]:
                    user_permission_list.append(rp[0])

            for sp in list(server_permission):
                if sp in user_permission_list:
                    s_perm_text += f"✅:{server_permission[sp]}"
                else:
                    not_sperm_text += f"❌:{server_permission[sp]}"
            for sp in list(member_permission):
                if sp in user_permission_list:
                    m_perm_text += f"✅:{member_permission[sp]}"
                else:
                    not_mperm_text += f"❌:{member_permission[sp]}"
            for sp in list(ch_permission):
                if sp in user_permission_list:
                    c_perm_text += f"✅:{ch_permission[sp]}"
                else:
                    not_cperm_text += f"❌:{ch_permission[sp]}"
            for sp in list(voice_permission):
                if sp in user_permission_list:
                    v_perm_text += f"✅:{voice_permission[sp]}"
                else:
                    not_vperm_text += f"❌:{voice_permission[sp]}"

            embed.add_field(name='サーバー全般', value=f'`{s_perm_text}`,`{not_sperm_text}`')
            embed.add_field(name='メンバー', value=f'`{m_perm_text}`,`{not_mperm_text}`')
            embed.add_field(name='テキストチャンネル', value=f'`{c_perm_text}`,`{not_cperm_text}`')
            embed.add_field(name='ボイス', value=f'`{v_perm_text}`,`{not_vperm_text}`')

            await ctx.send(embed=embed)

    @commands.command(name="avatar", description="ユーザーのアイコン")
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

    @commands.command(name="messageinfo", aliases=["msg", "message"], description="メッセージの情報")
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

    @commands.command(name="channelinfo", aliases=["chinfo"], description="```チャンネルの情報```",brief="誰でも")
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

        elif isinstance(target, discord.StageChannel):
            e = discord.Embed(name="チャンネル情報", description=f"{target.name}(ステージチャンネル)\nID:{target.id}")
            e.timestamp = target.created_at
            if target.category:
                e.add_field(name="所属するカテゴリ", value=f"{target.category.name}({target.category.id})")

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


    @commands.command(name="dir",usage="getobject member <ゆーざーid>",description="引数を選択した不和オブジェクトに変換します")
    async def get_object(self, ctx, object, arg, *, attr=None):
        """`誰でも`
        """
        object = object.replace(" ", "").lower()
        objects = {
            "member": commands.MemberConverter(),
            "user": commands.UserConverter(),
            "message": commands.MessageConverter(),
            "text": commands.TextChannelConverter(),
            "voice": commands.VoiceChannelConverter(),
            "category": commands.CategoryChannelConverter(),
            "invite": commands.InviteConverter(),
            "role": commands.RoleConverter(),
            "game": commands.GameConverter(),
            "colour": commands.ColourConverter(),
            "color": commands.ColorConverter(),
            "emoji": commands.EmojiConverter(),
            "partial": commands.PartialEmojiConverter(),
        }

        if object not in objects:
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    description="```Could not find object```",
                )
            )

        try:
            obj = await objects[object].convert(ctx, arg)
        except commands.BadArgument:
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(), description="```Conversion failed```"
                )
            )

        if attr:
            attributes = attr.split(".")
            try:
                for attribute in attributes:
                    obj = getattr(obj, attribute)
            except AttributeError:
                return await ctx.send(f"{obj} has no attribute {attribute}")
            return await ctx.send(f"```{obj}\n\n{dir(obj)}```")

        await ctx.send(f"```{obj}\n\n{dir(obj)}```")

    @commands.group(name="purges", description="システムコマンド")
    async def purges(self, ctx):
        """`Bot運営のみ`"""
        return

    @purges.command()
    async def all(self,ctx):
        if ctx.author.guild_permissions.administrator:
            await ctx.channel.purge()
            embed = discord.Embed(title="成功",description="",color=0x00ff7f)
            embed.add_field(name="すべてメッセージを削除しました。",value="残っている場合はもう一度実行してみてください。",inline=True)
            await ctx.channel.send(embed=embed)
        else:
            embed = discord.Embed(title="失敗",description="理由:権限不足",color=0xff0000)
            embed.add_field(name="__以下の権限があなたに振り分けされていますか？__",value="`管理者`",inline=True)
            await ctx.channel.send(embed=embed)

    @purges.command()
    async def amount(self, ctx, messages: int):
        if messages > 99:
            messages = 99
        await ctx.channel.purge(limit=messages + 1)
        await ctx.send(f'{messages} messages 削除しました', delete_after=3)






def setup(bot):
    bot.add_cog(information(bot))