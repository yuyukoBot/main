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

    @commands.Cog.listener()
    async def on_member_join(self,member:discord.Member):
        if member.guild.id == 847119998153261096:
            category_channel = self.bot.get_channel(850915412878688286)
            ow = {
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member.guild.me: discord.PermissionOverwrite(
                    read_messages=True, send_messages=True, manage_messages=True)
            }
            ch = await member.guild.create_text_channel(f'{member}-verfiy', overwrites=ow, topic=str(member.id),
                                                        position=0, category=category_channel)
            e = discord.Embed(title=f"{member}さん{member.guild}へようこそ～", description=f"ルール等読みましたら`y/agree`と入力してください")
            await ch.send(embed=e)



    @commands.command()
    async def agree(self,ctx):
        role = discord.utils.get(ctx.author.guild.roles, name="Server-Member")
        await ctx.author.add_roles(role)
        channel = self.bot.get_channel(850793112338038784)
        e = discord.Embed(title="ユーザー認証ログ", description=f"{ctx.author}さんが認証しました")
        await channel.send(embed=e)



    @commands.command()
    async def testserverinfo(self,ctx,*, guild_id: int = None):

        if guild_id is not None and await self.bot.is_owner(ctx.author):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return await ctx.send(f'Invalid Guild ID given.')
        else:
            guild = ctx.guild

        if not guild.chunked:
            async with ctx.typing():
                await guild.chunk(cache=True)

        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1

        e = discord.Embed(title="サーバー情報",color=0xfb00ff)
        e.add_field(name="サーバー名",value=f'{guild.name}({guild.id})')

        await ctx.send(embed=e)



def setup(bot):
    bot.add_cog(Server_Manage(bot))



