import discord
from asyncio import sleep

import json
from typing import Union
import logging
import textwrap
from datetime import time
import datetime
import asyncio
import DiscordUtils

from discord.ext import commands

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
        self.tracker = DiscordUtils.InviteTracker(bot)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.tracker.update_invite_cache(invite)

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
    async def on_member_remove(self, member):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM remove WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:
            cursor.execute(f"SELECT msg FROM remove WHERE guild_id = {member.guild.id}")
            result1 = cursor.fetchone()
            members = len(list(member.guild.members))
            mention = member.mention
            user = member.name
            guild = member.guild
            e = discord.Embed(title="ユーザー退出",
                              description=str(result1[0]).format(members=members, mention=mention, user=user,
                                                                 guild=guild))
            e.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            e.set_thumbnail(url=f"{member.avatar_url}")
            e.set_footer(text=f"{member.guild}", icon_url=f"{member.guild.icon_url}")
            channel = self.bot.get_channel(id=int(result[0]))

            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT channel_id FROM join WHERE guild_id = {member.guild.id}")
        result = cursor.fetchone()
        if result is None:
            return
        else:

            cursor.execute(f"SELECT msg FROM join WHERE guild_id = {member.guild.id}")
            result1 = cursor.fetchone()
            members = len(list(member.guild.members))
            inviter = await self.tracker.fetch_inviter(member)  # inviter is the member who invited
            data = await self.bot.invites.find(inviter.id)
            if data is None:
                data = {"_id": inviter.id, "count": 0, "userInvited": []}

            data["count"] += 1
            data["usersInvited"].append(member.id)
            await self.bot.invites.upsert(data)
            mention = member.mention
            user = member.name
            guild = member.guild
            e = discord.Embed(title="新規参加",
                              description=str(result1[0]).format(members=members, mention=mention, user=user,
                                                                 guild=guild))
            e.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            e.set_thumbnail(url=f"{member.avatar_url}")
            e.set_footer(text=f"{member.guild}", icon_url=f"{member.guild.icon_url}")
            e.add_field(name="test",value=f"Invited by: {inviter.mention}\nInvites: {data['count']}")
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
            cursor.execute(f"SELECT channel_id FROM join WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO join(guild_id,channel_id) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"Channel has been set to {channel.mention}")
            elif result is not None:
                sql = ("UPDATE join SET channel_id = ? WHERE guild_id = ?")
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
            cursor.execute(f"SELECT msg FROM join WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO join(guild_id,msg) VALUES(?,?)")
                val = (ctx.guild.id, text)
                await ctx.send(f"Channel has been set to {text}")
            elif result is not None:
                sql = ("UPDATE join SET msg = ? WHERE guild_id = ?")
                val = (text, ctx.guild.id)
                await ctx.send(f"Channel has been updated to `{text}`")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @commands.group()
    async def remove(self, ctx):
        await ctx.send('セットアップを完了してください:\nleave channel <#channel>\nleave text <message>')

    @remove.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        if ctx.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT channel_id FROM remove WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO remove(guild_id,channel_id) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"Channel has been set to {channel.mention}")
            elif result is not None:
                sql = ("UPDATE remove SET channel_id = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send(f"Channel has been updated to {channel.mention}")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")

    @remove.command()
    async def text(self, ctx, *, text):
        if ctx.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT msg FROM remove WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO remove(guild_id,msg) VALUES(?,?)")
                val = (ctx.guild.id, text)
                await ctx.send(f"Channel has been set to {text}")
            elif result is not None:
                sql = ("UPDATE remove SET msg = ? WHERE guild_id = ?")
                val = (text, ctx.guild.id)
                await ctx.send(f"Channel has been updated to `{text}`")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()


def setup(bot):
    bot.add_cog(welcome(bot))