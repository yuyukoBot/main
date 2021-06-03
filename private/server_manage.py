import os
import traceback

from datetime import datetime

from discord import Embed
import discord
from discord.ext import commands

class Server_Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.color = 0x5d00ff
        self.log_channel = self.bot.get_channel(820156651511349258)#テストチャンネル

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        channel = self.bot.get_channel(836558776253415495)
        if before.name != after.name:
            embed = discord.Embed(title="サーバーログ -ユーザーアップデート",
                          description="ユーザー名が変りました",
                          color=self.bot.color,
                          timestamp=datetime.utcnow())


            embed.add_field(name="変更前",value=before.name)
            embed.add_field(name="変更後",value=after.name)
            embed.set_thumbnail(url=after.avatar_url)






            await channel.send(embed=embed)

        if before.discriminator != after.discriminator:
            embed = Embed(title="Discriminator change",
                          colour=after.colour,
                          timestamp=datetime.utcnow())

            fields = [("Before", before.discriminator, False),
                      ("After", after.discriminator, False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await channel.send(embed=embed)

        if before.avatar_url != after.avatar_url:
            embed = Embed(title="Avatar change",
                          description="New image is below, old to the right.",
                          colour=self.log_channel.guild.get_member(after.id).colour,
                          timestamp=datetime.utcnow())

            embed.set_thumbnail(url=before.avatar_url)
            embed.set_image(url=after.avatar_url)


            await channel.send(embed=embed)



def setup(bot):
    bot.add_cog(Server_Manage(bot))



