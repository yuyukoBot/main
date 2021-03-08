import textwrap
import discord
from discord import Intents
import typing
import colorsys
import os
import random
import traceback
from utils.chat_formatting import box,pagify
from cog import Utils
import asyncio
import discord,fnmatch
from discord.ext import commands

import utils.json_loader

import random
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Optional
from typing import Union
import time
import platform
from discord.ext import commands
import io
from jishaku.codeblocks import Codeblock, codeblock_converter
from discord.ext.commands import clean_content
from discord import Embed
from discord.ext.commands import Cog
import os
import random
import traceback
from contextlib import redirect_stdout
import asyncio
from asyncio import sleep as _sleep

class Verified(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    def is_channel(ctx):
        return ctx.channel.id == 818337568885571624

    @commands.Cog.listener()
    async def on_member_join(self,member):
        if member.bot:
            bos = discord.utils.get(member.guild.roles, name="BOT")
            await member.add_roles(bos)
        else:
            unverified = discord.utils.get(member.guild.roles,
                                       name="未認証")
            await member.add_roles(unverified)



    @commands.command()
    @commands.check(is_channel)
    async def verify(self,ctx):
        unverified = discord.utils.get(ctx.guild.roles, name="未認証")
        if unverified in ctx.author.roles:
            msg = await ctx.send('DMに利用規約等載せています')
            await msg.add_reaction('✅')
            e = discord.Embed(title="**利用規約**",description="1:Discordの利用規約を守ってください\n2:#メインチャンネル、でのnsfw系のチャットをしないでください\n3:喧嘩など行う場合はDMで\n4:質問などがあれば　#質問で\n5:不具合があれば #不具合報告",color=0x5d00ff)
            e.add_field(name="認証方法",value="#認証 で`y/agree`を実行してください")
            await ctx.author.send(embed=e)

        else:
            await ctx.send('あなたは既に認証されています')

    @commands.command()
    @commands.check(is_channel)
    async def agree(self,ctx):
        unverified = discord.utils.get(ctx.guild.roles, name="未認証")
        verify = discord.utils.get(ctx.guild.roles, name="Yuyuko’s member")
        if unverified in ctx.author.roles:  # checks if the user running the command has the unveirifed role

            msg = await ctx.send('認証が完了しました')
            await msg.add_reaction('✅')
            await ctx.author.add_roles(verify)
            await ctx.author.remove_roles(unverified)

def setup(bot):
    bot.add_cog(Verified(bot))
