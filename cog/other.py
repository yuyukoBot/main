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

from collections import OrderedDict, deque, Counter
import datetime
import os

import codecs

import aiohttp
from bs4 import BeautifulSoup
import asyncio, discord
import random
import secrets
from io import BytesIO
import ast
import psutil
import functools
import inspect
from discord.ext.commands import clean_content
from discord import Embed
from discord.ext.commands import Cog
import sys
import json
import traceback
import wikipedia
import io
from contextlib import redirect_stdout
import re

import tracemalloc


class everyone(commands.Cog):
    """
    誰でも使えるコマンドです
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def translate(self, ctx, to_language, *, msg):
        """Translates words from one language to another. Do [p]help translate for more information.
        Usage:
        [p]translate <new language> <words> - Translate words from one language to another. Full language names must be used.
        The original language will be assumed automatically.
        """
        await ctx.message.delete()
        if to_language == "rot13":  # little easter egg
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name="Original", value=msg, inline=False)
            embed.add_field(name="ROT13", value=codecs.encode(msg, "rot_13"), inline=False)
            return await ctx.send("", embed=embed)
        async with self.bot.session.get(
                "https://gist.githubusercontent.com/astronautlevel2/93a19379bd52b351dbc6eef269efa0bc/raw/18d55123bc85e2ef8f54e09007489ceff9b3ba51/langs.json") as resp:
            lang_codes = await resp.json(content_type='text/plain')
        real_language = False
        to_language = to_language.lower()
        for entry in lang_codes:
            if to_language in lang_codes[entry]["name"].replace(";", "").replace(",", "").lower().split():
                language = lang_codes[entry]["name"].replace(";", "").replace(",", "").split()[0]
                to_language = entry
                real_language = True
        if real_language:
            async with self.bot.session.get("https://translate.google.com/m",
                                            params={"hl": to_language, "sl": "auto", "q": msg}) as resp:
                translate = await resp.text()
            result = str(translate).split('class="t0">')[1].split("</div>")[0]
            result = BeautifulSoup(result, "lxml").text
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name="Original", value=msg, inline=False)
            embed.add_field(name=language, value=result.replace("&amp;", "&"), inline=False)
            if result == msg:
                embed.add_field(name="Warning", value="This language may not be supported by Google Translate.")
            await ctx.send("", embed=embed)
        else:
            await ctx.send(self.bot.bot_prefix + "That's not a real language.")

    @commands.command()
    async def timer(self, ctx, seconds):
        try:
            secondint = int(seconds)
            if secondint > 1300:
                await ctx.send("300秒まで可能です")
                raise BaseException
            if secondint < 0 or secondint == 0:
                await ctx.send("I dont think im allowed to do negatives")
                raise BaseException
            message = await ctx.send("Timer: " + seconds)
            while True:
                secondint = secondint - 1
                if secondint == 0:
                    await message.edit(new_content=("Ended!"))
                    break
                await message.edit(new_content=("Timer: {0}".format(secondint)))
                await asyncio.sleep(1)
            await ctx.send(ctx.message.author.mention + " カウントダウン")
        except ValueError:
            await ctx.send("Must be a number!")

    @commands.command(name="say", aliases=["echo"], description="```任意の文章を送信します。```")
    async def say(self, ctx, *, arg):
        """`豆腐がしゃべります`"""
        await ctx.message.delete()
        if "<@" in arg or "@everyone" in arg or "@here" in arg:
            await ctx.send("```メンションはしないでください。```")
        else:
            await ctx.send(arg)

    @commands.command(name="source")
    async def source(self,ctx):
        embed = discord.Embed(title="ソースコード",description="https://github.com/Butachaan/yuyukochan")
        await ctx.send(embed=embed)

    @commands.command(name="invite", description="botの招待リンクを表示します")
    async def invite(self, ctx):
        """`誰でも`"""
        user = ctx.message.author
        embed = discord.Embed(title="invite-bot", color=0xb300ff)
        embed.set_thumbnail(
            url="https://images-ext-1.discordapp.net/external/p63_pSyVEDrhWnE2w87v2emUygjr2WA7AvD0m1mRaP8/%3Fsize%3D512/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
        embed.set_footer(text=user.name)
        embed.add_field(name="__**管理者権限**__",
                        value="https://discord.com/api/oauth2/authorize?client_id=757807145264611378&permissions=8&scope=bot")
        embed.add_field(name="__**Moderation機能**__",
                        value="https://discord.com/api/oauth2/authorize?client_id=757807145264611378&permissions=1544027255&scope=bot")
        embed.add_field(name="__**権限なし**__",
                        value="https://discord.com/api/oauth2/authorize?client_id=757807145264611378&permissions=0&scope=bot")
        await ctx.send(embed=embed)

    @commands.command(description="サポート鯖の情報です")
    async def official(self, ctx):
        """`誰でも`"""
        embed = discord.Embed(title="Yuyuko Support Server", url="https://discord.gg/xcwZYny",
                              description="幽々子のサポートサーバーです", color=0xb300ff)
        embed.set_thumbnail(
            url="https://images-ext-1.discordapp.net/external/p63_pSyVEDrhWnE2w87v2emUygjr2WA7AvD0m1mRaP8/%3Fsize%3D512/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
        embed.add_field(name="何かあればこちらへ", value="by creater", inline=True)
        embed.set_footer(text="幽々子")
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """`誰でも`"""
        msg = await ctx.send("`Pinging bot latency...`")
        times = []
        counter = 0
        embed = discord.Embed(title="More information:", description="Pinged 4 times and calculated the average.",
                              colour=discord.Colour(value=0x36393e))
        for _ in range(3):
            counter += 1
            start = time.perf_counter()
            await msg.edit(content=f"Pinging... {counter}/3")
            end = time.perf_counter()
            speed = round((end - start) * 1000)
            times.append(speed)
            embed.add_field(name=f"Ping {counter}:", value=f"{speed}ms", inline=True)

        embed.set_author(name="Pong!")
        embed.add_field(name="Bot latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Average speed",
                        value=f"{round((round(sum(times)) + round(self.bot.latency * 1000)) / 4)}ms")
        embed.set_footer(text=f"Estimated total time elapsed: {round(sum(times))}ms")
        await msg.edit(content=f":ping_pong: **{round((round(sum(times)) + round(self.bot.latency * 1000)) / 4)}ms**",
                       embed=embed)

    @commands.command(name="time", description="現在時刻を表示するよ！")
    async def time_(self,ctx):
        import locale
        locale.setlocale(locale.LC_CTYPE, "English_United States.932")
        await ctx.send(datetime.datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒"))



def setup(bot):
    bot.add_cog(everyone(bot))