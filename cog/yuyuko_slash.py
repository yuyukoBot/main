import discord
from discord.ext import commands

from discord_slash import cog_ext, SlashContext
from discord_slash.cog_ext import cog_slash

import os
import shutil
import re
import random
class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_slash(name="join", description="test")
    async def _test(self, ctx: SlashContext):
        embed = discord.Embed(title="embed test")
        await ctx.send(content="test", embeds=[embed])


    @commands.Cog.listener()
    async def on_slash_command(self, ctx:SlashContext):
        ch = self.bot.get_channel(757773097758883880)
        e = discord.Embed(title=f"スラッシュコマンド:{ctx.command}の実行", color=self.bot.ec)
        e.set_author(name=f"実行者:{str(ctx.author)}({ctx.author.id})",
                    icon_url=ctx.author.avatar_url_as(static_format="png"))
        e.set_footer(text=f"実行サーバー:{ctx.guild.name}({ctx.guild.id})",
                    icon_url=ctx.guild.icon_url_as(static_format="png"))
        e.add_field(name="実行チャンネル", value=ctx.channel.name)
        await ch.send(embed=e)

    guild_ids = [789032594456576001]

    @cog_slash(name="ping", guild_ids=guild_ids)
    async def _ping(self,ctx):  # Defines a new "context" (ctx) command called "ping."
        await ctx.send(f"Pong! ({cog_slash().latency * 1000}ms)")

def setup(bot):
    bot.add_cog(Slash(bot))