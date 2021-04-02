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


class welcome_leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT welcome_channel_id FROM ServerSetting WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            cursor.execute(f"SELECT welcome_msg FROM ServerSetting WHERE guild_id = {member.guild.id}")
            result1 = cursor.fetchone()
            members = len(list(member.guild.members))
            mention = member.mention
            user = member.name

            e = discord.Embed(title="新規参加")
            e.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            e.set_thumbnail(url=f"{member.avatar_url}")
            e.set_footer(text=f"{member.guild}", icon_url=f"{member.guild.icon_url}")
            channel = self.bot.get_channel(id=int(result[0]))


            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT remove_channel_id FROM ServerSetting WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            cursor.execute(f"SELECT remove_msg FROM ServerSetting WHERE guild_id = {member.guild.id}")
            result1 = cursor.fetchone()
            members = len(list(member.guild.members))
            mention = member.mention
            user = member.name
            guild = member.guild
            e = discord.Embed(title="メンバー退出")
            e.set_thumbnail(url=f"{member.avatar_url}")
            e.set_author(name=f"{member.name}",icon_url=f"{member.avatar_url}")
            e.set_footer(text=f"{member.guild}",icon_url=f"{member.guild.icon_url}")
            e.timestamp = datetime.datetime.utcnow()
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)








def setup(bot):
    bot.add_cog(welcome_leave(bot))