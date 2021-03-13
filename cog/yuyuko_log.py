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
import sqlite3
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

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {channel.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            e = discord.Embed(title="チャンネル削除", color=0x5d00ff)
            e.add_field(name="チャンネル名", value=channel.name)
            ch = discord.utils.get(channel.guild.channels, name="幽々子ログ")
            await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            ch = self.bot.get_channel(id=int(result[0]))
            if before.name != after.name:
                embed = discord.Embed(title="channel nameを変更しました", color=0x5d00ff)
                embed.add_field(name="設定前", value=f'`{before.name}`', inline=True)
                embed.add_field(name="設定後", value=f'`{after.name}`', inline=False)
                embed.add_field(name="現在のチャンネル名", value=after.name)
                embed.add_field(name="現在のトピック", value=after.topic)
                embed.add_field(name="nsfwかどうか", value=after.nsfw)
                embed.add_field(name="現在のカテゴリー", value=after.category)
                embed.add_field(name="低速モード", value=after.slowmode_delay)
                embed.add_field(name="タイプ", value=after.type)
                await ch.send(embed=embed)

            if before.topic != after.topic:
                e = discord.Embed(title="チャンネルのトピックが変わりました", color=0x5d00ff)
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
                e1 = discord.Embed(title="nsfwに設定(解除)しました", color=0x5d00ff)
                e1.add_field(name="設定前", value=f'`{before.nsfw}`')
                e1.add_field(name="設定後", value=f'`{after.nsfw}`')
                e1.add_field(name="現在のチャンネル名", value=after.name)
                e1.add_field(name="現在のトピック", value=after.topic)
                e1.add_field(name="nsfwかどうか", value=after.nsfw)
                e1.add_field(name="現在のカテゴリー", value=after.category)
                e1.add_field(name="低速モード", value=after.slowmode_delay)
                e1.add_field(name="タイプ", value=after.type)
                await ch.send(embed=e1)

            if before.category != after.category:
                e2 = discord.Embed(title="別のカテゴリーに移動しました", color=0x5d00ff)
                e2.add_field(name="設定前", value=f'`{before.category}`')
                e2.add_field(name="設定後", value=f'`{after.category}`')
                e2.add_field(name="現在のチャンネル名", value=after.name)
                e2.add_field(name="現在のトピック", value=after.topic)
                e2.add_field(name="nsfwかどうか", value=after.nsfw)
                e2.add_field(name="現在のカテゴリー", value=after.category)
                e2.add_field(name="低速モード", value=after.slowmode_delay)
                e2.add_field(name="タイプ", value=after.type)
                await ch.send(embed=e2)

            if before.slowmode_delay != after.slowmode_delay:
                e4 = discord.Embed(title="低速モードを設定しました", color=0x5d00ff)
                e4.add_field(name="設定前", value=f'`{before.slowmode_delay}秒`')
                e4.add_field(name="設定後", value=f'{after.slowmode_delay}秒')
                e4.add_field(name="現在のチャンネル名", value=after.name)
                e4.add_field(name="現在のトピック", value=after.topic)
                e4.add_field(name="nsfwかどうか", value=after.nsfw)
                e4.add_field(name="現在のカテゴリー", value=after.category)
                e4.add_field(name="低速モード", value=after.slowmode_delay)
                e4.add_field(name="タイプ", value=after.type)
                await ch.send(embed=e4)

            if before.type != after.type:
                e5 = discord.Embed(title="チャンネルのタイプを変更しました", color=0x5d00ff)
                e5.add_field(name="設定前", value=before.type)
                e5.add_field(name="設定後", value=after.type)
                e5.add_field(name="現在のチャンネル名", value=after.name)
                e5.add_field(name="現在のトピック", value=after.topic)
                e5.add_field(name="nsfwかどうか", value=after.nsfw)
                e5.add_field(name="現在のカテゴリー", value=after.category)
                e5.add_field(name="低速モード", value=after.slowmode_delay)
                e5.add_field(name="タイプ", value=after.type)
                await ch.send(embed=e5)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {channel.guild.id}")
        result = cursor.fetchone()
        if result is None:
            e = discord.Embed(title="チャンネル作成", timestamp=channel.created_at, color=0x5d00ff)
            e.add_field(name="チャンネル名", value=channel.mention)
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e)

        else:
             e = discord.Embed(title="チャンネル作成", timestamp=channel.created_at, color=0x5d00ff)
             e.add_field(name="チャンネル名", value=channel.mention)
             channel = self.bot.get_channel(id=int(result[0]))
             await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            if before.name != after.name:
                embed = discord.Embed(title="役職の名前が変わりました", color=0x5d00ff)

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
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=embed)

            if before.color != after.color:
                e = discord.Embed(title="役職の色が変わりました", color=0x5d00ff)
                e.add_field(name="id", value=after.id)
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
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

            if before.hoist != after.hoist:
                e1 = discord.Embed(title="役職を個別表示(非表示)にしました", color=0x5d00ff)

                e1.add_field(name="設定前", value=f'`{before.hoist}`')
                e1.add_field(name="設定後", value=f'`{after.hoist}`')
                e1.add_field(name="id", value=after.id)
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

                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e1)

            if before.mentionable != after.mentionable:
                e2 = discord.Embed(title="役職をメンション可能(不可能)にしました", color=0x5d00ff)

                e2.add_field(name="設定前", value=f'`{before.mentionable}`')
                e2.add_field(name="設定後", value=f'`{after.mentionable}`')
                e2.add_field(name="id", value=after.id)
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

                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e2)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {role.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            e = discord.Embed(title="役職の作成", color=0x5d00ff, timestamp=role.created_at)
            e.add_field(name="役職名", value=role.name)

            e.add_field(name="id", value=role.id)

            ch = self.bot.get_channel(id=int(result[0]))
            await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {role.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            e = discord.Embed(title="役職の削除", color=0x5d00ff)
            e.add_field(name="役職名", value=role.name)

            ch = self.bot.get_channel(id=int(result[0]))
            await ch.send(embed=e)


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:

            embed = discord.Embed(title="メッセージが編集されました",timestamp=after.created_at,description=f"<#{before.channel.id}>で<@!{before.author.id}>がメッセージを編集しました",colour=discord.Colour(0x5d00ff))




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
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {message.guild.id}")
            result = cursor.fetchone()
            if result is None:
                return
            else:
                e = discord.Embed(title="メッセージ削除", color=0x5d00ff)
                e.add_field(name="メッセージ", value=f'```{message.content}```', inline=False)
                e.add_field(name="メッセージ送信者", value=message.author.mention)
                e.add_field(name="メッセージチャンネル", value=message.channel.mention)
                e.add_field(name="メッセージのid", value=message.id)

                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)



    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {invite.guild.id}")
        result = cursor.fetchone()
        if result is None:
            e = discord.Embed(title="サーバー招待の作成", color=0x5d00ff)
            e.add_field(name="作成ユーザー", value=str(invite.inviter))
            e.add_field(name="使用可能回数", value=str(invite.max_uses))
            e.add_field(name="使用可能時間", value=str(invite.max_age))
            e.add_field(name="チャンネル", value=str(invite.channel.mention))
            e.add_field(name="コード", value=str(invite.code))
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)
        else:
            e = discord.Embed(title="サーバー招待の作成", color=0x5d00ff)
            e.add_field(name="作成ユーザー", value=str(invite.inviter))
            e.add_field(name="使用可能回数", value=str(invite.max_uses))
            e.add_field(name="使用可能時間", value=str(invite.max_age))
            e.add_field(name="チャンネル", value=str(invite.channel.mention))
            e.add_field(name="コード", value=str(invite.code))
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {after.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            if before.nick != after.nick:
                e = discord.Embed(title='ニックネームが変わりました', description=f"変更メンバー:{str(after)}", color=0x5d00ff)
                e.add_field(name="変更前", value=f'`{before.nick}`')
                e.add_field(name="変更後", value=f'`{after.nick}`')
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

            if before.roles != after.roles:
                e1 = discord.Embed(title="アップデート", description=f"変更メンバー:{str(after)}", color=0x5d00ff)
                if len(before.roles) > len(after.roles):
                    e1.add_field(name="変更内容", value="役職除去")
                    e1.add_field(name="役職", value=list(
                        set(before.roles) - set(after.roles))[0])
                else:
                    e1.add_field(name="変更内容", value="役職付与")
                    e1.add_field(name="役職", value=list(
                        set(after.roles) - set(before.roles))[0])
                    channel = self.bot.get_channel(id=int(result[0]))
                    await channel.send(embed=e1)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {user.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
            e = discord.Embed(title="ユーザーがBANされました", color=0x5d00ff)
            e.add_field(name="対象者", value=str(user))
            e.add_field(name="実行者", value=str(bl[0].user))
            e.set_footer(text=f"{guild.name}/{guild.id}")
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {after.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            if before.name != after.name:
                e = discord.Embed(title="サーバーの名前が変りました", color=0x5d00ff)
                e.add_field(name="変更前", value=f'`{before.name}`')
                e.add_field(name="変更後", value=f'`{after.name}`')
                e.add_field(name="AFKチャンネル", value=after.afk_channel)
                e.add_field(name="地域", value=after.region)
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e)

            if before.region != after.region:
                e1 = discord.Embed(title="サーバーの地域が変りました", color=0x5d00ff)
                e1.add_field(name="変更前", value=f'`{before.region}`')
                e1.add_field(name="変更後", value=f'`{after.region}`')
                e1.add_field(name="サーバー名", value=after.name)
                e1.add_field(name="AFKチャンネル", value=after.afk_channel)
                channel = self.bot.get_channel(id=int(result[0]))
                await channel.send(embed=e1)

        if before.afk_channel != after.afk_channel:
            e2 = discord.Embed(title="AFKチャンネルが変りました", color=0x5d00ff)
            e2.add_field(name="変更前", value=f'`{before.afk_channel}`')
            e2.add_field(name="変更前", value=f'`{after.afk_channel}`')
            e2.add_field(name="サーバー名", value=after.name)
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e2)

        if before.owner != after.owner:
            e3 = discord.Embed(title="サーバーの所有者が変りました", color=0x5d00ff)
            e3.add_field(name="変更前", value=f'`{before.owner}`')
            e3.add_field(name="変更前", value=f'`{after.owner}`')
            e3.add_field(name="サーバー名", value=after.name)
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e3)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
            e = discord.Embed(title="ユーザーのban解除", color=0x5d00ff)
            e.add_field(name="ユーザー名", value=str(user))
            e.add_field(name="Banしたときの実行者", value=str(bl[0].user))
            channel = self.bot.get_channel(id=int(result[0]))
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            cursor.execute(f"SELECT msg FROM log WHERE guild_id = {member.guild.id}")
            result1 = cursor.fetchone()
            members = len(list(member.guild.members))
            mention = member.mention
            user = member.name
            guild = member.guild
            e = discord.Embed(title="新規参加",
                              description=str(result1[0]).format(members=members, mention=mention, user=user,
                                                                 guild=guild))
            e.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            e.set_thumbnail(url=f"{member.avatar_url}")
            e.set_footer(text=f"{member.guild}", icon_url=f"{member.guild.icon_url}")
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)

    @commands.group()
    async def setting(self,ctx):
        e = discord.Embed(title="setting",description="y/setting log:指定したチャンネルにログを表示させます")
        await ctx.send(embed=e)


    @setting.command()
    async def log(self, ctx, channel: discord.TextChannel):
        if ctx.message.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT channel_id FROM log WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO log(guild_id,channel_id) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"Channel has been set to {channel.mention}")
            elif result is not None:
                sql = ("UPDATE log SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send(f"Channel has been updated to {channel.mention}")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()



def setup(bot):
    bot.add_cog(log(bot))