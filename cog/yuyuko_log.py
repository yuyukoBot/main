import discord
from asyncio import sleep

import json
from typing import Union
import logging
import textwrap
from datetime import time
import datetime
import asyncio
import random
from discord.ext import commands

from logging import DEBUG, getLogger
from contextlib import redirect_stdout
import textwrap
import traceback
import io
import sqlite3

logger = getLogger(__name__)


class log(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.bot.color = 0x5d00ff

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        bl = await channel.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete).flatten()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {channel.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            e = discord.Embed(title="-サーバーログ-チャンネル削除- ", color=0x5d00ff)
            e.add_field(name="チャンネル名", value=channel.name)
            e.add_field(name="実行者", value=str(bl[0].user))
            ch = self.bot.get_channel(id=int(result[0]))
            await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        bl = await after.audit_logs(limit=1, action=discord.AuditLogAction.channel_update).flatten()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            ch = self.bot.get_channel(id=int(result[0]))
            if before.name != after.name:
                embed = discord.Embed(title="-サーバーログ-チャンネル変更- ",description="チャンネルの名前を変更しました", color=0x5d00ff)
                embed.add_field(name="設定前", value=f'`{before.name}`', inline=True)
                embed.add_field(name="設定後", value=f'`{after.name}`', inline=False)
                embed.add_field(name="実行者", value=str(bl[0].user))
                embed.add_field(name="現在のチャンネル名", value=after.name)
                embed.add_field(name="現在のトピック", value=after.topic)
                embed.add_field(name="nsfwかどうか", value=after.nsfw)
                embed.add_field(name="現在のカテゴリー", value=after.category)
                embed.add_field(name="低速モード", value=after.slowmode_delay)
                embed.add_field(name="タイプ", value=after.type)
                await ch.send(embed=embed)

            if before.topic != after.topic:
                e = discord.Embed(title="-サーバーログ-チャンネル変更- ",description="チャンネルトピックを変更しました", color=0x5d00ff)
                e.add_field(name="設定前", value=f'`{before.topic}`')
                e.add_field(name="設定後", value=f'`{after.topic}`')
                e.add_field(name="現在のチャンネル名", value=after.name)
                e.add_field(name="現在のトピック", value=after.topic)
                e.add_field(name="nsfwかどうか", value=after.nsfw)
                e.add_field(name="現在のカテゴリー", value=after.category)
                e.add_field(name="低速モード", value=after.slowmode_delay)
                e.add_field(name="タイプ", value=after.type)
                await ch.send(embed=e)

            if before.nsfw != after.nsfw:
                e = discord.Embed(title="-サーバーログ-チャンネル変更- ",description="nsfwかどうかを変更しました", color=0x5d00ff)
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
                e = discord.Embed(title="-サーバーログ-チャンネル変更- ",description="カテゴリーを変更しました", color=0x5d00ff)
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
                e = discord.Embed(title="-サーバーログ-チャンネル変更- ",description="低速モードを設定しました", color=0x5d00ff)
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
                e = discord.Embed(title="-サーバーログ-チャンネル変更-",description="チャンネルタイプが変わりました", color=0x5d00ff)
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
        bl = await channel.audit_logs(limit=1, action=discord.AuditLogAction.channel_create).flatten()
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {channel.guild.id}")
        result = cursor.fetchone()
        if result is None:
            e = discord.Embed(title="-サーバーログ-チャンネル作成- ", timestamp=channel.created_at, color=0x5d00ff)
            e.add_field(name="チャンネル名", value=channel.mention)
            e.add_field(name="実行者", value=str(bl[0].user))
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e)

        else:
             e1 = discord.Embed(title="-サーバーログ-チャンネル作成- ", timestamp=channel.created_at, color=0x5d00ff)
             e1.add_field(name="チャンネル名", value=channel.mention)
             e1.add_field(name="実行者", value=str(bl[0].user))
             channel = self.bot.get_channel(id=int(result[0]))
             await channel.send(embed=e1)

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
        bl = await after.audit_logs(limit=1, action=discord.AuditLogAction.role_update).flatten()
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            pers = [f"`{c}`" for c in dict(before.permissions) if dict(before.permissions)[c] is True]
            pem = [f"`{c}`" for c in dict(after.permissions) if dict(after.permissions)[c] is True]
            if before.name != after.name:
                embed = discord.Embed(title="-サーバーログ-役職変更- ",description="役職名を変更しました", color=0x5d00ff)

                embed.add_field(name="名前", value=f'{after.name}({after.id})')
                embed.add_field(name="位置", value=after.position)
                embed.add_field(name="実行者", value=str(bl[0].user))
                if bool(after.hoist):
                    embed.add_field(name="個別表示ですか", value="はい")
                else:
                    embed.add_field(name="個別表示ですか", value="いいえ")

                if bool(after.mentionable):
                    embed.add_field(name="メンション可能", value="はい")
                else:
                    embed.add_field(name="メンション可能", value="いいえ")
                embed.add_field(name="変更後", value=rv(",".join(pem)))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=embed)

            if before.color != after.color:
                e = discord.Embed(title="-サーバーログ-役職変更- ",description="役職の色を変更しました", color=0x5d00ff)
                e.add_field(name="実行者", value=str(bl[0].user))
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
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

            if before.hoist != after.hoist:
                e1 = discord.Embed(title="-サーバーログ-役職変更- ",description="個別表示or非表示にしました", color=0x5d00ff)

                e1.add_field(name="設定前", value=f'`{before.hoist}`')
                e1.add_field(name="設定後", value=f'`{after.hoist}`')
                e1.add_field(name="実行者", value=str(bl[0].user))
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
                e1.add_field(name="変更後", value=rv(",".join(pem)))


                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e1)

            if before.mentionable != after.mentionable:
                e2 = discord.Embed(title="-サーバーログ-役職変更- ",description="メンション可能or不可能にしました", color=0x5d00ff)

                e2.add_field(name="設定前", value=f'`{before.mentionable}`')
                e2.add_field(name="設定後", value=f'`{after.mentionable}`')
                e2.add_field(name="実行者", value=str(bl[0].user))
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

                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e2)

            if before.permissions != after.permissions:

                e3 = discord.Embed(title="-サーバーログ-役職変更- ",description=f"役職の権限を変更しました\n変更メンバー:{str(after)}", color=0x5d00ff)
                e3.add_field(name="変更前",value=rv(",".join(pers)))
                e3.add_field(name="変更後",value=rv(",".join(pem)))
                e.add_field(name="実行者", value=str(bl[0].user))
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

                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e3)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        db = sqlite3.connect('main.sqlite')
        bl = await role.audit_logs(limit=1, action=discord.AuditLogAction.role_create).flatten()
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {role.guild.id}")
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
        bl = await role.audit_logs(limit=1, action=discord.AuditLogAction.role_delete).flatten()
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {role.guild.id}")
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
    async def on_message_edit(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:

            embed = discord.Embed(title="-サーバーログ-メッセージ変更-",timestamp=after.created_at,description=f"<#{before.channel.id}>で<@!{before.author.id}>がメッセージを編集しました",colour=discord.Colour(0x5d00ff))




            embed.set_author(name=f'{before.author.name}#{before.author.discriminator}', icon_url=before.author.avatar_url)
            embed.set_footer(text=f"Author ID:{before.author.id} • Message ID: {before.id}")
            embed.add_field(name='Before:', value=before.content, inline=False)
            embed.add_field(name="After:", value=after.content, inline=False)
            embed.add_field(name="メッセージのURL", value=after.jump_url)
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=embed)




    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.author.bot:
            bl = await message.audit_logs(limit=1, action=discord.AuditLogAction.message_delete).flatten()
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {message.guild.id}")
            result = cursor.fetchone()
            if result is None:
                return
            else:
                e = discord.Embed(title="-サーバーログ-メッセージ削除- ", color=0x5d00ff)
                e.add_field(name="メッセージ", value=f'```{message.content}```', inline=False)
                e.add_field(name="メッセージ送信者", value=message.author.mention)
                e.add_field(name="メッセージチャンネル", value=message.channel.mention)
                e.add_field(name="メッセージのid", value=message.id)
                e.add_field(name="実行者", value=str(bl[0].user))
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_reaction_clear(self,message, reactions):

        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {message.guild.id}")
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
    async def on_invite_create(self, invite):
        bl = await invite.audit_logs(limit=1, action=discord.AuditLogAction.invite_create).flatten()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {invite.guild.id}")
        result = cursor.fetchone()
        if result is None:
            e = discord.Embed(title="-サーバーログ-招待リンク作成- ", color=0x5d00ff)
            e.add_field(name="作成ユーザー", value=str(invite.inviter))
            e.add_field(name="使用可能回数", value=str(invite.max_uses))
            e.add_field(name="使用可能時間", value=str(invite.max_age))
            e.add_field(name="チャンネル", value=str(invite.channel.mention))
            e.add_field(name="コード", value=str(invite.code))
            e.add_field(name="実行者", value=str(bl[0].user))
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)
        else:
            e = discord.Embed(title="-サーバーログ-招待リンク作成- ", color=0x5d00ff)
            e.add_field(name="作成ユーザー", value=str(invite.inviter))
            e.add_field(name="使用可能回数", value=str(invite.max_uses))
            e.add_field(name="使用可能時間", value=str(invite.max_age))
            e.add_field(name="チャンネル", value=str(invite.channel.mention))
            e.add_field(name="コード", value=str(invite.code))
            e.add_field(name="実行者", value=str(bl[0].user))
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
            value = value.replace("`use_slash_commands`", "`スラッシュコマンドの使用")
            return value
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            bl = await after.audit_logs(limit=1, action=discord.AuditLogAction.member_update).flatten()
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
                e1 = discord.Embed(title="-サーバーログ-メンバー変更- ", description=f"役職を付与or剥奪しました\n変更メンバー:{str(after)}", color=0x5d00ff)
                if len(before.roles) > len(after.roles):
                    e1.add_field(name="変更内容", value="役職除去")
                    e1.add_field(name="役職", value=list(
                        set(before.roles) - set(after.roles))[0])
                else:
                    e1.add_field(name="変更内容", value="役職付与")
                    e1.add_field(name="役職", value=list(
                        set(after.roles) - set(before.roles))[0])
                    e1.add_field(name="実行者", value=str(bl[0].user))
                    e1.add_field(name="今の権限", value=rv(",".join(pem)))
                    channel = self.bot.get_channel(id=int(result[0]))
                    await channel.send(embed=e1)
            if before.guild_permissions != after.guild_permissions:

                e2 = discord.Embed(title="-サーバーログ-メンバー変更- ",description=f"権限を変更しました\n変更メンバー:{str(after)}", color=0x5d00ff)
                e2.add_field(name="変更前",value=rv(",".join(pers)))
                e2.add_field(name="変更後",value=rv(",".join(pem)))
                e2.add_field(name="実行者", value=str(bl[0].user))
                e2.add_field(name="役職",value=after.roles)
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e2)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user:discord.Member):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {user.guild.id}")
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
    async def on_voice_state_update(self,member:discord.Member, before, after):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {member.voice}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            if before.member != after.member:
                e = discord.Embed()
                e.add_field(name="変更前",value=before.member)
                e.add_field(name="変更前", value=after.member)


                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        await self.bot.wait_until_ready()
        bl = await after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update).flatten()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {after.id}")
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
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {guild.id}")
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
    async def on_member_join(self, member:discord.Member):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:

            e = discord.Embed(title="サーバーログ - ユーザーの参加",color=self.bot.color)
            e.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            if member.bot:
                e.add_field(name="Botですか", value="はい")
            else:
                e.add_field(name="Botですか",value="いいえ")
            shared = sum(g.get_member(member.id) is not None for g in self.bot.guilds)
            e.add_field(name="共通鯖数", value=shared)
            e.set_thumbnail(url=f"{member.avatar_url}")
            e.set_footer(text=member.guild, icon_url=member.guild.icon_url_as(format="png"))
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        await self.bot.wait_until_ready()
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {member.guild.id}")
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






def setup(bot):
    bot.add_cog(log(bot))