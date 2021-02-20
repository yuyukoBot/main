import discord
from asyncio import sleep

import json
from typing import Union
import logging
import textwrap
from datetime import time
import datetime
import asyncio
import random
from discord.ext import commands

class log(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_create(self,channel):
        e = discord.Embed(title="チャンネル作成", timestamp=channel.created_at, color=0x5d00ff)
        e.add_field(name="チャンネル名", value=channel.mention)
        channel = discord.utils.get(channel.guild.channels, name="幽々子ログ")
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_ban(self,g, user):
        guild = commands.get_guild(g.id)
        bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        e = discord.Embed(title="ユーザーのban", color=0x5d00ff)
        e.add_field(name="ユーザー名", value=str(user))
        e.add_field(name="実行者", value=str(bl[0].user))
        channel = discord.utils.get(commands.get.channels, name="幽々子ログ")
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_invite_create(self,invite):
        e = discord.Embed(title="サーバー招待の作成", color=0x5d00ff)
        e.add_field(name="作成ユーザー", value=str(invite.inviter))
        e.add_field(name="使用可能回数", value=str(invite.max_uses))
        e.add_field(name="使用可能時間", value=str(invite.max_age))
        e.add_field(name="チャンネル", value=str(invite.channel.mention))
        e.add_field(name="コード", value=str(invite.code))
        channel = discord.utils.get(invite.guild.channels, name="幽々子ログ")
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_user_update(self,before, after):
        if before.name != after.name:
            e = discord.Embed(title="ニックネーム", color=0x5d00ff, timestamp=datetime.utcnow())
            fields = [("Before", before.name, False), ("After", after.name, False)]

            for name, value, inline in fields:
                e.add_field(name=name, value=value, inline=inline)

            channel = discord.utils.get(before.get_channels, name="幽々子ログ")
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        if not message.author.bot:
            e = discord.Embed(title="メッセージ削除", color=0x5d00ff)
            e.add_field(name="メッセージ", value=f'```{message.content}```', inline=False)
            e.add_field(name="メッセージ送信者", value=message.author.mention)
            e.add_field(name="メッセージチャンネル", value=message.channel.mention)
            e.add_field(name="メッセージのid", value=message.id)

            channel = discord.utils.get(message.guild.channels, name="幽々子ログ")
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_update(self,before, after):
        print("1")
        if before.name != after.name:
            embed = discord.Embed(title="Role " + before.name + " renamed to " + after.name + ".", color=0x5d00ff)

            embed.set_author(name="名前が変りました")
            embed.add_field(name="id", value=after.id)
            embed.add_field(name="名前", value=after.name)
            embed.add_field(name="位置", value=after.position)
            channel = discord.utils.get(before.guild.channels, name="幽々子ログ")
            await channel.send(embed=embed)

        if before.color != after.color:
            e = discord.Embed(title="Role " + before.name + " change to " + after.name + ".", color=0x5d00ff)
            e.set_author(name="色が変りました")
            e.add_field(name="id", value=after.id)
            e.add_field(name="名前", value=after.name)
            e.add_field(name="位置", value=after.position)
            channel = discord.utils.get(before.guild.channels, name="幽々子ログ")
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_message_edit(self,before, after):

        embed = discord.Embed(
            title="メッセージが編集されました",
            timestamp=after.created_at,
            description=f"<#{before.channel.id}>で<@!{before.author.id}>がメッセージを編集しました",
            colour=discord.Colour(0x5d00ff)
        )
        embed.set_author(name=f'{before.author.name}#{before.author.discriminator}', icon_url=before.author.avatar_url)
        embed.set_footer(text=f"Author ID:{before.author.id} • Message ID: {before.id}")
        embed.add_field(name='Before:', value=before.content, inline=False)
        embed.add_field(name="After:", value=after.content, inline=False)
        embed.add_field(name="メッセージのURL", value=after.jump_url)
        channel = discord.utils.get(after.guild.channels, name="幽々子ログ")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self,role):
        e = discord.Embed(title="役職の作成", color=0x5d00ff, timestamp=role.created_at)
        e.add_field(name="役職名", value=role.name)

        e.add_field(name="id", value=role.id)

        ch = discord.utils.get(role.guild.channels, name="幽々子ログ")
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_delete(self,role):
        e = discord.Embed(title="役職の削除", color=0x5d00ff)
        e.add_field(name="役職名", value=role.name)

        ch = discord.utils.get(role.guild.channels, name="幽々子ログ")
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self,channel):
        e = discord.Embed(title="チャンネル削除", color=0x5d00ff)
        e.add_field(name="チャンネル名", value=channel.name)
        ch = discord.utils.get(channel.guild.channels, name="幽々子ログ")
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_update(self,before, after):
        channel = discord.utils.get(before.guild.channels, name="幽々子ログ")
        embed = discord.Embed(title="Channel Name Updated", description="チャンネルがアップデートしました", color=0x5d00ff)
        embed.add_field(name="Old name", value=f"The old name was: {before}.", inline=True)
        embed.add_field(name="New name", value=f"The old name was: {after}.", inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(before, after):
        if before.voice.voice_channel is None and after.voice.voice_channel is not None:
            for channel in before.server.channels:
                if channel.name == 'あざ':
                    await commands.send_message(channel, "Howdy")

    @commands.group(invoke_without_command=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def new(self, ctx):
        await ctx.send("Invalid sub-command passed.")

    @new.command(
        name="category",
        description="Create a new category",
        usage="<role> <Category name>",
    )
    @commands.has_guild_permissions(manage_channels=True)
    async def category(self, ctx, role: discord.Role, *, name):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True),
        }
        category = await ctx.guild.create_category(name=name, overwrites=overwrites)
        await ctx.send(f"Hey dude, I made {category.name} for ya!")

    @new.command(
        name="channel",
        description="Create a new channel",
        usage="<role> <channel name>",
    )
    @commands.has_guild_permissions(manage_channels=True)
    async def channel(self, ctx, role: discord.Role, *, name):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True),
        }
        channel = await ctx.guild.create_text_channel(
            name=name,
            overwrites=overwrites,
            category=self.bot.get_channel(707945693582590005),
        )
        await ctx.send(f"Hey dude, I made {channel.name} for ya!")

    @commands.group(invoke_without_command=True)
    @commands.has_guild_permissions(manage_channels=True)
    async def delete(self, ctx):
        await ctx.send("Invalid sub-command passed")

    @delete.command(
        name="category", description="Delete a category", usage="<category> [reason]"
    )
    @commands.has_guild_permissions(manage_channels=True)
    async def _category(self, ctx, category: discord.CategoryChannel, *, reason=None):
        await category.delete(reason=reason)
        await ctx.send(f"hey! I deleted {category.name} for you")

    @delete.command(
        name="channel", description="Delete a channel", usage="<channel> [reason]"
    )
    @commands.has_guild_permissions(manage_channels=True)
    async def _channel(self, ctx, channel: discord.TextChannel = None, *, reason=None):
        channel = channel or ctx.channel
        await channel.delete(reason=reason)
        await ctx.send("hey! I deleted ")

    @commands.command(aliases=["chedit", "che"], description="コマンドを実行したチャンネル名を変更するよ！\nチャンネルを管理できる人のみ！")
    async def channeledit(self,ctx, channelname):
        if (
                ctx.guild.me.top_role < ctx.author.top_role and ctx.author.guild_permissions.manage_channelss) or ctx.guild.owner == ctx.author:
            await ctx.channel.edit(name=f"{channelname}")
            e = discord.Embed(title="操作成功", description=f'チャンネル名を変更しました\n現在のチャンネル名:{channelname}',
                              color=ctx.author.color)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(title="実行エラー", description="権限がありません", color=0xff0000)
            await ctx.send(embed=e)

    @commands.command(aliases=["rcr"], description="役職を作成するよ！\n役職を管理できる人のみ！")
    async def rolecreate(self,ctx, rolename):
        if (
                ctx.guild.me.top_role < ctx.author.top_role and ctx.author.guild_permissions.manage_roles) or ctx.guild.owner == ctx.author:
            role = await ctx.guild.create_role(name=rolename)
            e = discord.Embed(title="操作成功", description=f'{role.mention}を作成したよ～', color=ctx.author.color)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(title="実行エラー", description="私は役職を作成する権限を持ってないよ～", color=0xff0000)
            await ctx.send(embed=e)

    @commands.command(aliases=["rdel"], description="役職を削除するよ！\n役職を管理できる人のみ！")
    async def roledelete(self,ctx, role: discord.Role):
        if (
                ctx.guild.me.top_role < ctx.author.top_role and ctx.author.guild_permissions.manage_roles) or ctx.guild.owner == ctx.author:
            await role.delete()
            e = discord.Embed(title="操作成功", description=f'{role.name}を削除したよ～', color=ctx.author.color)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(title="実行エラー", description="君はコマンドを実行する権限を持ってないよ～", color=0xff0000)
            await ctx.send(embed=e)

    @commands.Cog.listener()
    async def on_message(self, message):
        def _check(m):
            return (m.author == message.author
                    and len(m.mentions)
                    and (datetime.utcnow() - m.created_at).seconds < 60)

        if not message.author.bot:
            if len(list(filter(lambda m: _check(m), self.bot.cached_messages))) >= 3:
                await message.channel.send("Don't spam mentions!", delete_after=10)
                unmutes = await self.mute_members(message, [message.author], 5, reason="Mention spam")

                if len(unmutes):
                    await sleep(5)
                    await self.unmute_members(message.guild, [message.author])

    @commands.Cog.listener()
    async def on_member_join(self,member):
        # On member joins we find a channel called general and if it exists,
        # send an embed welcoming them to our guild
        role = discord.utils.get(member.guild.roles, name="shhh")
        channel = discord.utils.get(member.guild.text_channels, name="メインチャット")
        if channel:
            embed = discord.Embed(
                description=f'ようこそ{member.mention}さん。{member.guild}へ、#mcid でmcidを記入してください',
                color=0x5d00ff,

            )

            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="ユーザー名", value=member.name)
            embed.add_field(name="ユーザーid", value=member.id)
            embed.add_field(name="Joined", value=member.joined_at)
            embed.add_field(name="Created", value=member.created_at)
            embed.add_field(name="User Serial", value=len(list(member.guild.members)))
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        # On member remove we find a channel called general and if it exists,
        # send an embed saying goodbye from our guild-
        channel = discord.utils.get(member.guild.text_channels, name="メインチャット")
        if channel:
            embed = discord.Embed(
                description=f'さようなら{member.name}さん',
                color=0x5d00ff,
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="ユーザー名", value=member.name)
            embed.add_field(name="ユーザーid", value=member.id)
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self,before, after):
        if before.display_name != after.display_name:
            e = discord.Embed(title="ニックネームが変わりました", color=0x5d00ff)

            fields = [("Before", before.display_name, False),
                      ("After", after.display_name, False)]

            for name, value, inline in fields:
                e.add_field(name=name, value=value, inline=inline)
            e.timestamp = datetime.datetime.utcnow()

            channel = discord.utils.get(after.guild.text_channels, name="幽々子ログ")
            await channel.send(embed=e)

        elif before.roles != after.roles:
            e = discord.Embed(title='役職が付与(剥奪)されました', color=0x5d00ff)

            fields = [("Before", ", ".join([r.mention for r in before.roles]), False),
                      ("After", ", ".join([r.mention for r in after.roles]), False)]
            for name, value, inline in fields:
                e.add_field(name=name, value=value, inline=inline)
            e.timestamp = datetime.datetime.utcnow()
            channel = discord.utils.get(after.guild.text_channels, name="幽々子ログ")
            await channel.send(embed=e)


def setup(bot):
    bot.add_cog(log(bot))