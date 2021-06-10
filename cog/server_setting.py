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
        self.bot.color = 0x5d00ff

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
        await ctx.send_help(ctx.command)

    @settings.command()
    async def _reactrole(self, ctx, emoji, role: discord.Role, messageid):

        if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            msg = await ctx.channel.fetch_message(messageid)
            await msg.add_reaction(emoji)
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute("INSERT INTO reactrole VALUES (?,?,?,?,?)", (role.name, role.id, str(emoji), messageid, ctx.guild.id))
            db.commit()
            await ctx.message.delete()





    @settings.command(description="指定したチャンネルにログを送信します")
    async def log(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id,log_channel) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                e = discord.Embed(title="ログチャンネルをセットしました")
                e.add_field(name="取得できる内容",value="ユーザーの退出(入出)や役職の付与剥奪\nチャンネル(役職/メッセージの作成削除や設定変更等...")
                e.add_field(name="該当チャンネル",value=channel.mention)
                await ctx.send(embed=e)

            elif result is not None:
                sql = ("UPDATE ServerSetting SET log_channel = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                e = discord.Embed(title="ログチャンネルをセットしました")
                e.add_field(name="取得できる内容", value="ユーザーの退出(入出)や役職の付与剥奪\nチャンネル(役職/メッセージの作成削除や設定変更等...")
                e.add_field(name="該当チャンネル", value=channel.mention)
                await ctx.send(embed=e)
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



    @settings.command(description="T指定したチャンネルにログを送信します")
    async def welcome_channel(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT welcome_channel_id FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id,welcome_channel_id) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"{channel.mention}をウェルカムチャンネルとして設定しました")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET welcome_channel_id = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send(f"{channel.mention}をウェルカムチャンネルとして設定しました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

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

    @settings.command(name='list')
    async def _list(self, ctx):
        import sqlite3
        conn = sqlite3.connect('main.sqlite')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM ServerSetting WHERE guild_id = ?', (ctx.guild.id,))
        data = cursor.fetchall()
        if not data:
            return await ctx.send('データが見つかりませんでした')
        settings = data[0]
        embed = discord.Embed(title='Server Settings')
        embed.add_field(name='ログチャンネル', value=self.bot.get_channel(int(settings[4])).mention if settings[4] else 'なし')
        embed.add_field(name='Welcomeチャンネル', value=self.bot.get_channel(int(settings[1])).mention if settings[1] else 'なし')
        await ctx.send(embed=embed)



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

    @commands.Cog.listener()
    async def on_reaction_add(self, payload):
        if payload.member.bot:
            return
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM reactrole WHERE guild_id = ?", (payload.guild_id,))
        data = cursor.fetchall()

        if not data:
            return
        else:
            for x in data:
                if x[2] == str(payload.emoji) and int(x[3]) == payload.message_id:
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x[1])
                    await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_reaction_remove(self, payload):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM reactrole WHERE guild_id = ?", (payload.guild_id,))
        data = cursor.fetchall()

        if not data:
            return
        else:
            for x in data:
                if str(payload.emoji)[-1:] in x[2] and int(x[3]) == payload.message_id:
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x[1])
                    await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)




def setup(bot):
    bot.add_cog(ServerSetting(bot))

