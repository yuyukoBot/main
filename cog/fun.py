import textwrap
from discord import Intents
import typing
import aiohttp
from datetime import datetime, timedelta
from typing import Optional
from typing import Union
import time
import platform
from discord.ext import commands
from platform import python_version
from discord import __version__ as discord_version
from asyncio import sleep
import json
from discord.utils import get
import os
import logging
import asyncio, discord
import random
import secrets
from io import BytesIO
import ast

import functools
import inspect
from discord.ext.commands import clean_content
from discord import Embed
from discord.ext.commands import Cog
import sys
import DiscordUtils
Intents = discord.Intents.default()
Intents.members = True
Intents.presences = True
import aiomojang

class fun(commands.Cog, name="Fun"):

    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)

    @commands.command(aliases=["ps"], description="password")
    async def password(self, ctx, nbytes: int = 18):
        """ Generates a random password string for you
        This returns a random URL-safe text string, containing nbytes random bytes.
        The text is Base64 encoded, so on average each byte results in approximately 1.3 characters.
        """
        if nbytes not in range(3, 1401):
            return await ctx.send("I only accept any numbers between 3-1400")
        if hasattr(ctx, 'guild') and ctx.guild is not None:
            await ctx.send(f"Sending you a private message with your random generated password **{ctx.author.name}**")
        await ctx.author.send(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(nbytes)}")

    @commands.command(aliases=["minecraftstats", "statsminecraft", "mcstats"])  # Get information on a player.
    async def mojang(self, ctx, player: str):
        profile = aiomojang.Player(player)
        try:
            embed = discord.Embed(title=f"<:success:761297849475399710> Information on {player}: ",
                                  color=ctx.author.color)
            embed.add_field(name="Player's name: ", value=player)  # Because doing profile.name will raise an error.
            embed.add_field(name="Player's uuid: ", value=await profile.uuid, inline=False)
            embed.set_image(url=await profile.get_skin())
            embed.set_author(name=player, icon_url=await profile.get_skin())
            embed.set_footer(text="Requested by {}".format(ctx.author.name), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        except aiomojang.exceptions.ApiException:
            return await ctx.send(f"No user with the name {player} was found.")

    @commands.command(aliases=["mchistory"])  # Name history command
    async def history(self, ctx, player: str):
        profile = aiomojang.Player(player)
        embed = discord.Embed(title=f"{player}'s name history: ", color=discord.Colour.blue())
        i = 1
        for x in await profile.get_history():
            embed.add_field(name=f"Name #{i}: ", value=x['name'])  # Iterate through the names.
            i = i + 1
        await ctx.send(embed=embed)

    @commands.command(aliases=["sl"], description="スロット")
    async def slot(self, ctx):
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

        if (a == b == c):
            await ctx.send(f"{slotmachine} All matching, you won! 🎉")
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(f"{slotmachine} 2 in a row, you won! 🎉")
        else:
            await ctx.send(f"{slotmachine} No match, you lost 😢")




def setup(bot):
    bot.add_cog(fun(bot))