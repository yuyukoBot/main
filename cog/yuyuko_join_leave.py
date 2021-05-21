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
import DiscordUtils
from itertools import product
logger = getLogger(__name__)


class welcome_leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)
        self.invites = []

    async def update_invites_cache(self):
        guild = await self.bot.fetch_guild(self.guild_id)
        self.invites = await guild.invites()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT welcome_channel_id FROM ServerSetting WHERE guild_id = {member.guild.id}")
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
            cursor.execute(f"SELECT welcome_msg FROM ServerSetting WHERE guild_id = {member.guild.id}")
            result1 = cursor.fetchone()
            members = len(list(member.guild.members))
            mention = member.mention
            user = member.name

            e = discord.Embed(title="新規参加")
            e.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            e.set_thumbnail(url=f"{member.avatar_url}")
            e.add_field(name="招待した人", value=inviter)
            e.add_field(name="招待コード", value=invite_code)
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