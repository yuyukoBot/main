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


class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM welcome WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:

            cursor.execute(f"SELECT msg FROM welcome WHERE guild_id = {member.guild.id}")
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
    async def welcome(self, ctx):
        await ctx.send('セットアップを完了してください:\nwelcome channel <#channel>\nwelcome text <message>')

    @welcome.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        if ctx.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT channel_id FROM welcome WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO welcome(guild_id,channel_id) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"Channel has been set to {channel.mention}")
            elif result is not None:
                sql = ("UPDATE welcome SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send(f"Channel has been updated to {channel.mention}")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")

    @welcome.command()
    async def text(self, ctx, *, text):
        if ctx.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT msg FROM welcome WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO welcome(guild_id,msg) VALUES(?,?)")
                val = (ctx.guild.id, text)
                await ctx.send(f"Channel has been set to {text}")
            elif result is not None:
                sql = ("UPDATE welcome SET msg = ? WHERE guild_id = ?")
                val = (text, ctx.guild.id)
                await ctx.send(f"Channel has been updated to `{text}`")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()


def setup(bot):
    bot.add_cog(welcome(bot))