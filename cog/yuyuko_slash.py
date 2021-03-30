import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="test")
    async def _test(self, ctx: SlashContext):
        embed = discord.Embed(title="embed test")
        await ctx.send(content="test", embeds=[embed])

    guild_ids = 759386170689585213

    @cog_ext.cog_slash(
        name="ttest",
        description="Sends message.",
        guild_ids=guild_ids
    )
    async def ttest(elf,ctx: SlashContext):
        embed = discord.Embed(title="embed test")
        await ctx.send(content='test', embeds=[embed])

def setup(bot):
    bot.add_cog(Slash(bot))