import discord
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
import re
logger = getLogger(__name__)


class ServerSetting(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group()
    async def vc(self,ctx):
        return

    @vc.command()
    async def role(self, ctx, role: discord.Role):
        if ctx.message.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT voice_role FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO  ServerSetting(guild_id,voice_role) VALUES(?,?)")
                val = (ctx.guild.id, role.id)
                await ctx.send("vcロールをセットしました")
            elif result is not None:
                sql = ("UPDATE  ServerSetting SET voice_role = ? WHERE guild_id = ?")
                val = (role.id, ctx.guild.id)
                await ctx.send("ロールをアップデートしました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @vc.command()
    async def channel(self, ctx, channel: discord.VoiceChannel):
        if ctx.message.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT voice_channel FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO  ServerSetting(guild_id,voice_channel) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send("チャンネルをセットしました")
            elif result is not None:
                sql = ("UPDATE  ServerSetting SET voice_role = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send("チャンネルをアップデートしました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT welcome_role FROM ServerSetting WHERE guild_id = {member.guild.id}")
        role = cursor.fetchone()
        if role is None:
            return
        else:
            member.add_roles(role)


    @commands.group()
    async def settings(self, ctx):
        return

    @settings.command(description="指定したチャンネルにログを送信します")
    async def log(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE log_guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(log_guild_id,log_channel) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"{channel.mention}をログチャンネルとして設定しました")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET log_channel = ? WHERE log_guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send(f"{channel.mention}をログチャンネルとして設定しました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @settings.command(description="指定したチャンネルにウェルカムメッセージを設定します")
    async def welcome_text(self, ctx, *, text):
        """`メッセージの管理`"""
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT welcome_msg FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id, welcome_msg) VALUES(?,?)")
                val = (ctx.guild_id, text)
                await ctx.send(f"{text}にセットしました")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET welcome_msg = ? WHERE guild_id = ?")
                val = (text, ctx.guild.id)
                await ctx.send(f"{text}にアップデートしました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @settings.command(description="チャンネルを設定します")
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.author.guild_permissions.manage_channels or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT welcome_channel_id FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id,welcome_channel_id) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"Channel has been set to {channel.mention}")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET welcome_channel_id = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send(f"Channel has been updated to {channel.mention}")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")

    @settings.command(description="退出時のメッセージを設定します")
    async def remove_text(self, ctx, *, text):
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            """`メッセージの管理`"""
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT welcome_msg FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id, welcome_msg) VALUES(?,?)")
                val = (ctx.guild_id, text)
                await ctx.send(f"{text}にセットしました")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET welcome_msg = ? WHERE guild_id = ?")
                val = (text, ctx.guild.id)
                await ctx.send(f"{text}にアップデートしました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @settings.command(description="参加時に付与する役職を設定します")
    async def welcome_role(self, ctx, role: discord.Role):
        if ctx.author.guild_permissions.manage_roles or ctx.author.id == 478126443168006164:
            """`役職の管理`"""
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT welcome_role FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id,welcome_role) VALUES(?,?)")
                val = (ctx.guild.id, role.id)
                await ctx.send("セットしました")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET welcome_role = ? WHERE guild_id = ?")
                val = (role.id, ctx.guild.id)
                await ctx.send(f"アップデート")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @settings.command(description="退出時のチャンネルを設定します")
    async def remove_channel(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT remove_channel_id FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id,remove_channel_id) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"Channel has been set to {channel.mention}")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET remove_channel_id = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send(f"Channel has been updated to {channel.mention}")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")


    @settings.command(description="入出時のチャンネルをリセットします")
    async def welcome_reset_channel(self,ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            cursor.execute("DELETE FROM ServerSetting "
                                      "WHERE guild_id = ? AND welcome_channel_id = ?",
                                      [int(ctx.guild.id), int(channel.id)])

            await ctx.send(f"{channel.mention}を削除しました")
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")

    @settings.command(description="退出時のチャンネルをリセットします")
    async def remove_reset_channel(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            cursor.execute("DELETE FROM ServerSetting "
                           "WHERE guild_id = ? AND remove_channel_id  = ?",
                           [int(ctx.guild.id), int(channel.id)])

            await ctx.send(f"{channel.mention}を削除しました")
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")

    @settings.command(description="ログチャンネルをリセットします")
    async def log_reset(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.author.guild_permissions.manage_channels or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            cursor.execute("DELETE FROM ServerSetting "
                           "WHERE log_guild_id = ? AND log_channel  = ?",
                           [int(ctx.guild.id), int(channel.id)])

            await ctx.send(f"{channel.mention}を削除しました")
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")






def setup(bot):
    bot.add_cog(ServerSetting(bot))

