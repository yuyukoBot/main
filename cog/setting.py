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

    @commands.command()
    async def setting(self, ctx, channel: discord.TextChannel):
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