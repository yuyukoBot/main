import asyncio
from datetime import timedelta

import aiohttp
import discord
from discord.ext import tasks, commands

from utils.config import get_config

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.command(brief="Performs a HTTP request", usage="http <address>")
    async def http(self, ctx, address: str) -> None:
        """
        Performs a HTTP request to the specified address
        :param ctx: commands.Context
        :param address: Address to make request to
        :return: HTTP status code
        """
        if not address.startswith("http"):
            address = f"http://{address}"

        timeout = get_config("http_timeout")

        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
        ) as session:
            try:
                async with session.get(address) as res:
                    await ctx.send(
                        f"Recieved response code: {res.status} ({res.reason})"
                    )
            except asyncio.TimeoutError:
                await ctx.send(f"Request timed out after {timeout} seconds")
            except aiohttp.ClientError:
                await ctx.send(f"Could not establish a connection to {address}")
def setup(bot):
    bot.add_cog(Ping(bot))