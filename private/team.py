import os
import traceback

import discord
from discord.ext import commands

from util.group import MakeTeam


class Teamdivision(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command()
    async def team(self,ctx, specified_num=2):
        make_team = MakeTeam()
        remainder_flag = 'true'
        msg = make_team.make_party_num(ctx, specified_num, remainder_flag)
        await ctx.channel.send(msg)

    # メンバー数が均等にはならないチーム分け
    @commands.command()
    async def team_norem(self,ctx, specified_num=2):
        make_team = MakeTeam()
        msg = make_team.make_party_num(ctx, specified_num)
        await ctx.channel.send(msg)

    # メンバー数を指定してチーム分け
    @commands.command()
    async def group(self,ctx, specified_num=1):
        make_team = MakeTeam()
        msg = make_team.make_specified_len(ctx, specified_num)
        await ctx.channel.send(msg)


def setup(bot):
    bot.add_cog(Teamdivision(bot))
