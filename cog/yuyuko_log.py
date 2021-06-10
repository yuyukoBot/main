import discord
from asyncio import sleep

import json
from typing import Union
from discord import Color, Embed, Guild, Member, User
import logging
import textwrap
from datetime import time
import datetime
import asyncio
import random
from itertools import product

import tools
from discord.ext import commands

from logging import DEBUG, getLogger
from contextlib import redirect_stdout
import textwrap
import traceback
import io
import sqlite3
import DiscordUtils
logger = getLogger(__name__)


class log(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.bot.color = 0x5d00ff
        self.tracker = DiscordUtils.InviteTracker(bot)
        self.invites = []

    async def update_invites_cache(self):
        guild = await self.bot.fetch_guild(self.guild_id)
        self.invites = await guild.invites()

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {messages.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            guild = messages[0].channel.guild
            channel = self.bot.get_channel(id=int(result[0]))
            e = discord.Embed(title="-サーバーログ-メッセージ一括削除- ",description=f"**Bulk messages deleted in {messages[0].channel.mention}, {len(messages)} messages deleted.**", color=0x5d00ff)
            e.set_author(name=f"{guild.name}", icon_url=guild.icon.url if guild.icon.url is not None else '')
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await self.bot.wait_until_ready()
        if not message.author.bot:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {message.guild.id}")
            result = cursor.fetchone()
            if result is None:
                return
            else:
                e = discord.Embed(title="-サーバーログ-メッセージ削除- ", color=0x5d00ff)
                e.add_field(name="メッセージ", value=f'```{message.content}```', inline=False)
                e.add_field(name="メッセージ送信者", value=message.author.mention)
                e.add_field(name="メッセージチャンネル", value=message.channel.mention)
                e.add_field(name="メッセージのid", value=message.id)
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:

            embed = discord.Embed(title="-サーバーログ-メッセージ変更-", timestamp=after.created_at,
                                  description=f"<#{before.channel.id}>で<@!{before.author.id}>がメッセージを編集しました",
                                  colour=discord.Colour(0x5d00ff))

            embed.set_author(name=f'{before.author.name}#{before.author.discriminator}',
                             icon_url=before.author.avatar_url)
            embed.set_footer(text=f"Author ID:{before.author.id} • Message ID: {before.id}")
            embed.add_field(name='Before:', value=before.content, inline=False)
            embed.add_field(name="After:", value=after.content, inline=False)

            embed.add_field(name="メッセージのURL", value=after.jump_url)
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        bl = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {channel.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            e = discord.Embed(title="-サーバーログ-チャンネル削除- <:delete_channel:840907400394833930> ", color=0x5d00ff)
            e.add_field(name="チャンネル名", value=channel.name)
            e.add_field(name="実行者", value=str(bl[0].user))
            ch = self.bot.get_channel(id=int(result[0]))
            await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        bl = await after.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update).flatten()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            ch = self.bot.get_channel(id=int(result[0]))
            if before.name != after.name:
                if isinstance(after, discord.TextChannel):
                    embed = discord.Embed(title="<:update_channel:840914594058600448> -サーバーログ-テキストチャンネル変更- ",description="チャンネルの名前を変更しました", color=0x5d00ff)
                    embed.add_field(name="設定前", value=f'`{before.name}`', inline=True)
                    embed.add_field(name="設定後", value=f'`{after.name}`', inline=False)
                    embed.add_field(name="実行者", value=str(bl[0].user))
                    embed.add_field(name="現在のチャンネル名", value=after.name)
                    embed.add_field(name="現在のトピック", value=after.topic)
                    embed.add_field(name="nsfwかどうか", value=after.nsfw)
                    embed.add_field(name="現在のカテゴリー", value=after.category)
                    embed.add_field(name="低速モード", value=after.slowmode_delay)
                    await ch.send(embed=embed)
                elif isinstance(after, discord.VoiceChannel):
                    e = discord.Embed(title="<:update_channel:840914594058600448> -サーバーログ-ボイスチャンネル変更- ",description="チャンネルの名前を変更しました", color=0x5d00ff)
                    e.add_field(name="設定前", value=f'`{before.name}`', inline=True)
                    e.add_field(name="設定後", value=f'`{after.name}`', inline=False)
                    e.add_field(name="実行者", value=str(bl[0].user))
                    mbs = ""
                    for m in after.members:
                        if len(mbs + f"`{m.name}`,") >= 1020:
                            mbs = mbs + f"他"
                            break
                        else:
                            mbs = mbs + f"`{m.name}`,"
                    if mbs != "":
                        e.add_field(name=f"参加可能なメンバー({len(after.members)}人)", value=mbs, inline=False)

                    await ch.send(embed=e)
                elif isinstance(after, discord.StageChannel):
                    e = discord.Embed(title="<:update_channel:840914594058600448> -サーバーログ-カテゴリ変更- ",description="カテゴリーの名前を変更しました", color=0x5d00ff)
                    e.add_field(name="設定前", value=f'`{before.name}`', inline=True)
                    e.add_field(name="設定後", value=f'`{after.name}`', inline=False)
                    e.add_field(name="実行者", value=str(bl[0].user))
                    e.add_field(name="現在のチャンネル名", value=after.name)
                    mbs = ""
                    for m in after.members:
                        if len(mbs + f"`{m.name}`,") >= 1020:
                            mbs = mbs + f"他"
                            break
                        else:
                            mbs = mbs + f"`{m.name}`,"
                    if mbs != "":
                        e.add_field(name=f"参加可能なメンバー({len(after.members)}人)", value=mbs, inline=False)
                    await ch.send(embed=e)

            if before.topic != after.topic:
                e = discord.Embed(title="<:update_channel:840914594058600448> -サーバーログ-チャンネル変更- ",description="チャンネルトピックを変更しました", color=0x5d00ff)
                e.add_field(name="設定前", value=f'`{before.topic}`')
                e.add_field(name="設定後", value=f'`{after.topic}`')
                e.add_field(name="実行者", value=str(bl[0].user))
                e.add_field(name="現在のチャンネル名", value=after.name)
                e.add_field(name="現在のトピック", value=after.topic)
                e.add_field(name="nsfwかどうか", value=after.nsfw)
                e.add_field(name="現在のカテゴリー", value=after.category)
                e.add_field(name="低速モード", value=after.slowmode_delay)
                e.add_field(name="タイプ", value=after.type)
                await ch.send(embed=e)

            if before.nsfw != after.nsfw:
                    e = discord.Embed(title="<:update_channel:840914594058600448> -サーバーログ-チャンネル変更- ",description="nsfwかどうかを変更しました", color=0x5d00ff)
                    if before.nsfw:
                        e.add_field(name="設定前", value=f'`はい`')
                    else:
                        e.add_field(name="設定後", value=f'`いいえ`')
                    e.add_field(name="実行者", value=str(bl[0].user))
                    e.add_field(name="現在のチャンネル名", value=after.name)
                    e.add_field(name="現在のトピック", value=after.topic)
                    e.add_field(name="nsfwかどうか", value=after.nsfw)
                    e.add_field(name="現在のカテゴリー", value=after.category)
                    e.add_field(name="低速モード", value=after.slowmode_delay)
                    e.add_field(name="タイプ", value=after.type)
                    await ch.send(embed=e)

            if before.category != after.category:
                e = discord.Embed(title="<:update_channel:840914594058600448> -サーバーログ-チャンネル変更- ",description="カテゴリーを変更しました", color=0x5d00ff)
                e.add_field(name="設定前", value=f'`{before.category}`')
                e.add_field(name="設定後", value=f'`{after.category}`')
                e.add_field(name="実行者", value=str(bl[0].user))
                e.add_field(name="現在のチャンネル名", value=after.name)
                e.add_field(name="現在のトピック", value=after.topic)
                e.add_field(name="nsfwかどうか", value=after.nsfw)
                e.add_field(name="現在のカテゴリー", value=after.category)
                e.add_field(name="低速モード", value=after.slowmode_delay)
                e.add_field(name="タイプ", value=after.type)
                await ch.send(embed=e)

            if before.slowmode_delay != after.slowmode_delay:
                e = discord.Embed(title="<:update_channel:840914594058600448> -サーバーログ-チャンネル変更- ",description="低速モードを設定しました", color=0x5d00ff)
                e.add_field(name="設定前", value=f'`{before.slowmode_delay}秒`')
                e.add_field(name="設定後", value=f'{after.slowmode_delay}秒')
                e.add_field(name="実行者", value=str(bl[0].user))
                e.add_field(name="現在のチャンネル名", value=after.name)
                e.add_field(name="現在のトピック", value=after.topic)
                e.add_field(name="nsfwかどうか", value=after.nsfw)
                e.add_field(name="現在のカテゴリー", value=after.category)
                e.add_field(name="低速モード", value=after.slowmode_delay)
                e.add_field(name="タイプ", value=after.type)
                await ch.send(embed=e)

            if before.type != after.type:
                e = discord.Embed(title="<:update_channel:840914594058600448> -サーバーログ-チャンネル変更-",description="チャンネルタイプが変わりました", color=0x5d00ff)
                e.add_field(name="設定前", value=before.type)
                e.add_field(name="設定後", value=after.type)
                e.add_field(name="実行者", value=str(bl[0].user))
                e.add_field(name="現在のチャンネル名", value=after.name)
                e.add_field(name="現在のトピック", value=after.topic)
                e.add_field(name="nsfwかどうか", value=after.nsfw)
                e.add_field(name="現在のカテゴリー", value=after.category)
                e.add_field(name="低速モード", value=after.slowmode_delay)
                e.add_field(name="タイプ", value=after.type)
                await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        db = sqlite3.connect('main.sqlite')
        bl = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create).flatten()
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {channel.guild.id}")
        result = cursor.fetchone()
        if result is None:
            e = discord.Embed(title="<:create_channel:840913176819662858> -サーバーログ-チャンネル作成- ", timestamp=channel.created_at, color=0x5d00ff)
            e.add_field(name="チャンネル名", value=channel.mention)
            e.add_field(name="実行者", value=str(bl[0].user))
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e)

        else:
            ch = self.bot.get_channel(id=int(result[0]))
            if isinstance(channel, discord.TextChannel):
                e = discord.Embed(title="<:create_channel:840913176819662858> -サーバーログ -テキストチャンネル作成",
                                  color=self.bot.color)
                e.add_field(name="チャンネル名", value=f'{channel}({channel.id})')
                if channel.category:
                    e.add_field(name="所属するカテゴリ", value=f"{channel.category.name}({channel.category.id})")
                e.add_field(name="チャンネルトピック", value=channel.topic or "なし")
                if not channel.slowmode_delay == 0:
                    e.add_field(name="スローモードの時間", value=f"{channel.slowmode_delay}秒")
                e.add_field(name="NSFW指定有無", value=channel.is_nsfw())
                await ch.send(embed=e)
            elif isinstance(channel, discord.VoiceChannel):
                e = discord.Embed(title="<:create_channel:840913176819662858> -サーバーログ-ボイスチャンネル作成- ",
                                  timestamp=channel.created_at, color=0x5d00ff)
                e.add_field(name="チャンネル名", value=channel.mention)
                e.add_field(name="実行者", value=str(bl[0].user))
                if not channel.user_limit == 0:
                    e.add_field(name="ユーザー数制限", value=f"{channel.user_limit}人")
                mbs = ""
                for m in channel.members:
                    if len(mbs + f"`{m.name}`,") >= 1020:
                        mbs = mbs + f"他"
                        break
                    else:
                        mbs = mbs + f"`{m.name}`,"
                if mbs != "":
                    e.add_field(name=f"参加可能なメンバー({len(channel.members)}人)", value=mbs, inline=False)
                await ch.send(embed=e)
            elif isinstance(channel, discord.CategoryChannel):
                e = discord.Embed(title="<:create_channel:840913176819662858> -サーバーログ-カテゴリ-作成- ",
                                  timestamp=channel.created_at, color=0x5d00ff)
                e.add_field(name="チャンネル名", value=channel.mention)
                e.add_field(name="実行者", value=str(bl[0].user))
                mbs = ""
                for c in channel.channels:
                    if c.type is discord.ChannelType.news:
                        if "NEWS" in channel.guild.features:
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
                    e.add_field(name=f"所属するチャンネル({len(channel.channels)}チャンネル)", value=mbs, inline=False)
                await ch.send(embed=e)

            elif isinstance(channel, discord.StageChannel):
                e = discord.Embed(title="<:create_channel:840913176819662858> -サーバーログ-ステージチャンネル作成- ",
                                  timestamp=channel.created_at,color=self.bot.color)
                e.add_field(name="チャンネル名",value=channel.mention)
                e.add_field(name="実行者", value=str(bl[0].user))
                if channel.category:
                    e.add_field(name="所属するカテゴリ", value=f"{channel.category.name}({channel.category.id})")

                if not channel.user_limit == 0:
                    e.add_field(name="ユーザー数制限", value=f"{channel.user_limit}人")
                mbs = ""
                for m in channel.members:
                    if len(mbs + f"`{m.name}`,") >= 1020:
                        mbs = mbs + f"他"
                        break
                    else:
                        mbs = mbs + f"`{m.name}`,"
                if mbs != "":
                    e.add_field(name=f"参加可能なメンバー({len(channel.members)}人)", value=mbs, inline=False)
                await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
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
            value = value.replace("`use_slash_commands`", "`スラッシュコマンドの使用`")
            return value
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            pers = [f"`{c}`" for c in dict(before.permissions) if dict(before.permissions)[c] is True]
            pem = [f"`{c}`" for c in dict(after.permissions) if dict(after.permissions)[c] is True]
            bl = await after.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update).flatten()
            if before.name != after.name:
                embed = discord.Embed(title="-サーバーログ-役職変更- ",description="役職名を変更しました", color=0x5d00ff)

                embed.add_field(name="名前", value=f'{after.name}({after.id})')
                embed.add_field(name="位置", value=after.position)
                if bool(after.hoist):
                    embed.add_field(name="個別表示ですか", value="はい")
                else:
                    embed.add_field(name="個別表示ですか", value="いいえ")

                if bool(after.mentionable):
                    embed.add_field(name="メンション可能", value="はい")
                else:
                    embed.add_field(name="メンション可能", value="いいえ")
                embed.add_field(name="変更後", value=rv(",".join(pem)))
                embed.add_field(name="実行者", value=str(bl[0].user))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=embed)

            if before.color != after.color:
                e = discord.Embed(title="-サーバーログ-役職変更- ",description="役職の色を変更しました", color=0x5d00ff)
                e.add_field(name="名前", value=f'{after.name}({after.id})')
                e.add_field(name="位置", value=after.position)
                if bool(after.hoist):
                    e.add_field(name="個別表示ですか", value="はい")
                else:
                    e.add_field(name="個別表示ですか", value="いいえ")

                if bool(after.mentionable):
                    e.add_field(name="メンション可能", value="はい")
                else:
                    e.add_field(name="メンション可能", value="いいえ")
                e.add_field(name="変更後", value=rv(",".join(pem)))
                e.add_field(name="実行者", value=str(bl[0].user))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

            if before.hoist != after.hoist:
                e1 = discord.Embed(title="-サーバーログ-役職変更- ",description="個別表示or非表示にしました", color=0x5d00ff)

                e1.add_field(name="設定前", value=f'`{before.hoist}`')
                e1.add_field(name="設定後", value=f'`{after.hoist}`')
                e1.add_field(name="名前", value=f'{after.name}({after.id})')
                e1.add_field(name="位置", value=after.position)
                if bool(after.hoist):
                    e1.add_field(name="個別表示ですか", value="はい")
                else:
                    e1.add_field(name="個別表示ですか", value="いいえ")

                if bool(after.mentionable):
                    e1.add_field(name="メンション可能", value="はい")
                else:
                    e1.add_field(name="メンション可能", value="いいえ")
                e1.add_field(name="実行者", value=str(bl[0].user))
                e1.add_field(name="変更後", value=rv(",".join(pem)))


                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e1)

            if before.mentionable != after.mentionable:
                e2 = discord.Embed(title="-サーバーログ-役職変更- ",description="メンション可能or不可能にしました", color=0x5d00ff)

                e2.add_field(name="設定前", value=f'`{before.mentionable}`')
                e2.add_field(name="設定後", value=f'`{after.mentionable}`')
                e2.add_field(name="名前", value=f'{after.name}({after.id})')
                e2.add_field(name="位置", value=after.position)
                if bool(after.hoist):
                    e2.add_field(name="個別表示ですか", value="はい")
                else:
                     e2.add_field(name="個別表示ですか", value="いいえ")

                if bool(after.mentionable):
                    e2.add_field(name="メンション可能", value="はい")
                else:
                    e2.add_field(name="メンション可能", value="いいえ")
                e2.add_field(name="変更後", value=rv(",".join(pem)))
                e2.add_field(name="実行者", value=str(bl[0].user))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e2)

            if before.permissions != after.permissions:

                e3 = discord.Embed(title="-サーバーログ-役職変更- ",description=f"役職の権限を変更しました\n変更メンバー:{str(after)}", color=self.bot.color)
                e3.add_field(name="変更前",value=rv(",".join(pers)))
                e3.add_field(name="変更後",value=rv(",".join(pem)))
                e3.add_field(name="名前", value=f'{after.name}({after.id})')
                e3.add_field(name="位置", value=after.position)
                if bool(after.hoist):
                    e3.add_field(name="個別表示ですか", value="はい")
                else:
                    e3.add_field(name="個別表示ですか", value="いいえ")

                if bool(after.mentionable):
                    e3.add_field(name="メンション可能", value="はい")
                else:
                    e3.add_field(name="メンション可能", value="いいえ")
                e3.add_field(name="実行者", value=str(bl[0].user))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e3)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {role.guild.id}")
        bl = await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create).flatten()
        result = cursor.fetchone()
        if result is None:
            return
        else:
            e = discord.Embed(title="-サーバーログ-役職作成- ", color=0x5d00ff, timestamp=role.created_at)
            e.add_field(name="役職名", value=f"{role.name}({role.id})")
            e.add_field(name="実行者", value=str(bl[0].user))
            ch = self.bot.get_channel(id=int(result[0]))
            await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        bl = await role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete).flatten()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {role.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            e = discord.Embed(title="-サーバーログ-役職削除- ", color=0x5d00ff)
            e.add_field(name="役職名", value=role.name)
            e.add_field(name="実行者", value=str(bl[0].user))
            ch = self.bot.get_channel(id=int(result[0]))
            await ch.send(embed=e)




    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.bot.wait_until_ready()
        await self.tracker.update_invite_cache(invite)
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {invite.guild.id}")
        result = cursor.fetchone()
        if result is None:
            e = discord.Embed(title="-サーバーログ-招待リンク作成- ", color=0x5d00ff)
            e.add_field(name="作成ユーザー", value=str(invite.inviter))
            e.add_field(name="使用可能回数", value=str(invite.max_uses))
            e.add_field(name="使用可能時間", value=str(invite.max_age))
            e.add_field(name="チャンネル", value=str(invite.channel.mention))
            e.add_field(name="コード", value=str(invite.code))
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)
        else:
            e = discord.Embed(title="-サーバーログ-招待リンク作成- ", color=0x5d00ff)
            e.add_field(name="作成ユーザー", value=str(invite.inviter))
            e.add_field(name="使用可能回数", value=str(invite.max_uses))
            e.add_field(name="使用可能時間", value=str(invite.max_age))
            e.add_field(name="チャンネル", value=str(invite.channel.mention))
            e.add_field(name="コード", value=str(invite.code))
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.tracker.update_guild_cache(guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.tracker.cache_invites()

    @commands.Cog.listener()
    async def on_voice_state_update(self,member:discord.Member, before, after):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            ch = self.bot.get_channel(id=int(result[0]))


            if before.channel !=after.channel:
                if after.channel is None:
                    e = discord.Embed(title="サーバーログ -ボイスチャンネル退出",color=self.bot.color)
                    e.add_field(name="該当チャンネル",value=before.channel.mention)
                    e.add_field(name="抜けたメンバー",value=member.mention)


                    e.set_thumbnail(url=member.avatar_url_as(format="png"))
                    await ch.send(embed=e)
                else:
                    e = discord.Embed(title="サーバーログ -ボイスチャンネル入出",color=self.bot.color)
                    e.add_field(name="該当チャンネル",value=after.channel.mention)
                    e.add_field(name="入ったメンバー",value=member.mention)
                    e.set_thumbnail(url=member.avatar_url_as(format="png"))
                    await ch.send(embed=e)

            if before.mute != after.mute:
                e = discord.Embed(title="サーバーログ -サーバーミュート設定(解除)",color=self.bot.color)
                e.add_field(name="該当ユーザー",value=member.mention)
                e.add_field(name="該当チャンネル", value=after.channel.mention)
                await ch.send(embed=e)

            if before.deaf != after.deaf:
                e = discord.Embed(title="サーバーログ -サーバー側スピーカーミュート")
                e.add_field(name="該当ユーザー",value=member.mention)
                e.add_field(name="該当チャンネル",value=after.channel.mention)
                await ch.send(embed=e)



            if before.self_mute != after.self_mute:
                e = discord.Embed(title="test",description={member})
                await ch.send(embed=e)








    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        await self.bot.wait_until_ready()
        bl = await after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update).flatten()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {after.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            if before.name != after.name:
                e = discord.Embed(title="-サーバーログ-サーバー変更- ",description="サーバー名を変更しました", color=0x5d00ff)
                e.add_field(name="変更前", value=f'`{before.name}`')
                e.add_field(name="変更後", value=f'`{after.name}`')
                e.add_field(name="AFKチャンネル", value=after.afk_channel)
                e.add_field(name="地域", value=after.region)
                e.add_field(name="実行者", value=str(bl[0].user))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

            if before.region != after.region:
                e1 = discord.Embed(title="-サーバーログ-サーバー変更- ",description="サーバー地域を変更しました", color=0x5d00ff)
                e1.add_field(name="変更前", value=f'`{before.region}`')
                e1.add_field(name="変更後", value=f'`{after.region}`')
                e.add_field(name="実行者", value=str(bl[0].user))
                e1.add_field(name="サーバー名", value=after.name)
                e1.add_field(name="AFKチャンネル", value=after.afk_channel)
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e1)

        if before.afk_channel != after.afk_channel:
            e2 = discord.Embed(title="-サーバーログ-サーバー変更- ",description="AFKチャンネルを変更しました", color=0x5d00ff)
            e2.add_field(name="変更前", value=f'`{before.afk_channel}`')
            e2.add_field(name="変更前", value=f'`{after.afk_channel}`')
            e.add_field(name="実行者", value=str(bl[0].user))
            e2.add_field(name="サーバー名", value=after.name)
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e2)

        if before.owner != after.owner:
            e3 = discord.Embed(title="-サーバーログ-サーバー変更- ",description="サーバーの所有者を変更しました", color=0x5d00ff)
            e3.add_field(name="変更前", value=f'`{before.owner}`')
            e3.add_field(name="変更前", value=f'`{after.owner}`')
            e.add_field(name="実行者", value=str(bl[0].user))
            e3.add_field(name="サーバー名", value=after.name)
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e3)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user:discord.Member):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
            e = discord.Embed(title="-サーバーログ-メンバーのBan解除- ", color=0x5d00ff)
            e.add_field(name="ユーザー名", value=str(user))
            e.add_field(name="Banしたときの実行者", value=str(bl[0].user))
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e)



    @commands.Cog.listener()
    async def on_member_update(self, before, after):
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
            value = value.replace("`use_slash_commands`", "`スラッシュコマンドの使用`")
            return value
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            bl = await after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update).flatten()
            pers = [f"`{c}`" for c in dict(before.guild_permissions) if dict(before.guild_permissions)[c] is True]
            pem = [f"`{c}`" for c in dict(after.guild_permissions) if dict(after.guild_permissions)[c] is True]
            if before.nick != after.nick:

                e = discord.Embed(title="-サーバーログ-メンバー変更- ", description=f"ニックネームを変更しました\n変更メンバー:{str(after)}", color=0x5d00ff)
                e.add_field(name="変更前", value=f'`{before.nick}`')
                e.add_field(name="変更後", value=f'`{after.nick}`')
                e.add_field(name="実行者", value=str(bl[0].user))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

            if before.roles != after.roles:
                bls = await after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update).flatten()

                old_roles = set(before.roles)
                new_roles = set(after.roles)
                removed_roles = old_roles - new_roles
                added_roles = new_roles - old_roles
                action_type = "剥奪" if removed_roles else "付与"
                description = (
                    f"**Role:** {removed_roles.pop().mention if removed_roles else added_roles.pop().mention}\n"
                    f"**Mention:** {after.mention}"
                )
                e1 = discord.Embed(title=f"-サーバーログ-メンバーの役職{action_type}- ", description=description,
                                   color=0x5d00ff)

                e1.add_field(name="今の権限", value=rv(",".join(pem)))
                e1.add_field(name="実行者", value=str(bls[0].user))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e1)
            if before.guild_permissions != after.guild_permissions:
                blse = await after.guild.audit_logs(limit=1, action=discord.AuditLogActionCategory.update).flatten()

                e2 = discord.Embed(title="-サーバーログ-メンバー変更- ",description=f"権限を変更しました\n変更メンバー:{str(after)}", color=0x5d00ff)
                e2.add_field(name="変更前",value=rv(",".join(pers)))
                e2.add_field(name="変更後",value=rv(",".join(pem)))
                e2.add_field(name="役職",value=after.roles)
                e2.add_field(name="実行者", value=str(blse[0].user))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e2)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user:discord.Member):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
            e = discord.Embed(title="-サーバーログ-メンバーBan- ", color=0x5d00ff)
            e.add_field(name="対象者", value=str(user))
            e.add_field(name="実行者", value=str(bl[0].user))
            e.set_footer(text=f"{guild.name}/{guild.id}")
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_user_update(self, user_before: User, user_after: User):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {user_after.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            ch = self.bot.get_channel(id=int(result[0]))

            if user_before.name != user_after.name:
                e = discord.Embed(title="サーバーログ-ユーザーアップデート",description=f"ニックネームを変更しました\n変更メンバー:{str(user_after)}")

                e.add_field(name="変更後",value=user_after.name)
                await ch.send(embed=e)



    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {member.guild.id}")

        result = cursor.fetchone()
        if result is None:
            return
        else:
            invites_after_join = await member.guild.invites()

            def find_used_invite(invites_before, invites_after):
                for invites in product(invites_before, invites_after):
                    if (invites[0].code == invites[1].code
                            and invites[0].uses < invites[1].uses):
                        return invites[0]

                # If invite can't be found
                return None

            invite_used = find_used_invite(self.invites, invites_after_join)
            inviter = invite_used.inviter.mention if invite_used else "Unknown"
            invite_code = invite_used.code if invite_used else "Unknown"



            embed = discord.Embed(
                title="サーバーログ -ユーザー参加",
                timestamp=member.joined_at
            )
            embed.add_field(name="ユーザー名",value=member.mention)
            embed.add_field(name="招待した人", value=inviter)
            embed.add_field(name="招待コード", value=invite_code)
            bl = await member.guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add).flatten()
            if member.bot:
                embed.add_field(name="botを追加したユーザー", value=str(bl[0].user))
            embed.set_thumbnail(url=member.avatar_url)
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:

            e = discord.Embed(title="サーバーログ - ユーザーの退出",color=self.bot.color)
            e.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            if member.bot:
                e.add_field(name="Botですか", value="はい")
            else:
                e.add_field(name="Botですか", value="いいえ")
            shared = sum(g.get_member(member.id) is not None for g in self.bot.guilds)
            e.add_field(name="役職", value=[i.name for i in member.roles])
            e.add_field(name="共通鯖数", value=shared)
            e.set_thumbnail(url=f"{member.avatar_url}")
            e.set_footer(text=member.guild, icon_url=member.guild.icon_url_as(format="png"))
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_reaction_clear(self, message, reactions):

        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {message.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            e = discord.Embed(title="-サーバーログ-リアクション削除- ", color=0x5d00ff)
            e.add_field(name="該当メッセージ", value=message.content or "(本文なし)")
            e.add_field(name="リアクション", value=[str(i) for i in reactions])

            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        await self.bot.wait_until_ready()
        message = reaction.message
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {reaction.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            ch = self.bot.get_channel(id=int(result[0]))
            e = discord.Embed(title="-サーバーログ-リアクション剥奪- ", color=self.bot.color)
            e.add_field(name="該当メッセージと絵文字", value=f"{message}:{reaction.emoji}")
            e.add_field(name="リアクションを剥奪したユーザー", value=user)
            await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        await self.bot.wait_until_ready()
        message = reaction.message
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {reaction.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            ch = self.bot.get_channel(id=int(result[0]))
            e = discord.Embed(title="-サーバーログ-リアクション剥奪- ", color=self.bot.color)
            e.add_field(name="該当メッセージと絵文字", value=f"{message}:{reaction.emoji}")
            e.add_field(name="リアクションを剥奪したユーザー", value=user)
            await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self,before,after):
        if before.name != after.name:
            e = discord.Embed(title="サーバーログ -絵文字アップデート")
            e.add_field(name="変更前",value=before.name)
            e.add_field(name="変更跡",value=after.name)
            e.set_thumbnail(url=after.url)
            ch = self.bot.get_channel(757773097758883880)
            await ch.send(embed=e)



def setup(bot):
    bot.add_cog(log(bot))