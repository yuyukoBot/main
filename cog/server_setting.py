import discord
from typing import Union
import logging
import textwrap
from datetime import time

from datetime import datetime, timedelta
from discord_components import DiscordComponents,Button,ButtonStyle,InteractionType, Select, SelectOption
import datetime
import asyncio
import random
from discord.ext import commands
from logging import DEBUG, getLogger
from contextlib import redirect_stdout
import textwrap
import traceback
import io
import sqlite3
import re
logger = getLogger(__name__)
from discord.ext import menus

class ServerSetting(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.bot.color = 0x5d00ff

    @commands.group()
    async def vc(self,ctx):
        return

    @vc.command()
    async def role(self, ctx, role: discord.Role):
        if ctx.message.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT voice_role FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO  ServerSetting(guild_id,voice_role) VALUES(?,?)")
                val = (ctx.guild.id, role.id)
                await ctx.send("vcロールをセットしました")
            elif result is not None:
                sql = ("UPDATE  ServerSetting SET voice_role = ? WHERE guild_id = ?")
                val = (role.id, ctx.guild.id)
                await ctx.send("ロールをアップデートしました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @vc.command()
    async def channel(self, ctx, channel: discord.VoiceChannel):
        if ctx.message.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT voice_channel FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO  ServerSetting(guild_id,voice_channel) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send("チャンネルをセットしました")
            elif result is not None:
                sql = ("UPDATE  ServerSetting SET voice_role = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send("チャンネルをアップデートしました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT welcome_role FROM ServerSetting WHERE guild_id = {member.guild.id}")
        role = cursor.fetchone()
        if role is None:
            return
        else:
            member.add_roles(role)


    @commands.group()
    async def settings(self, ctx):

        await ctx.send_help(ctx.command)

    @settings.command()
    async def _reactrole(self, ctx, emoji, role: discord.Role, messageid):

        if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            msg = await ctx.channel.fetch_message(messageid)
            await msg.add_reaction(emoji)
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute("INSERT INTO reactrole VALUES (?,?,?,?,?)", (role.name, role.id, str(emoji), messageid, ctx.guild.id))
            db.commit()
            await ctx.message.delete()






    @settings.command(description="指定したチャンネルにウェルカムメッセージを設定します")
    async def welcome_text(self, ctx, *, text):
        """`メッセージの管理`"""
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT welcome_msg FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id, welcome_msg) VALUES(?,?)")
                val = (ctx.guild_id, text)
                await ctx.send(f"{text}にセットしました")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET welcome_msg = ? WHERE guild_id = ?")
                val = (text, ctx.guild.id)
                await ctx.send(f"{text}にアップデートしました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()


    @settings.command(description="退出時のメッセージを設定します")
    async def remove_text(self, ctx, *, text):
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            """`メッセージの管理`"""
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT welcome_msg FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id, welcome_msg) VALUES(?,?)")
                val = (ctx.guild_id, text)
                await ctx.send(f"{text}にセットしました")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET welcome_msg = ? WHERE guild_id = ?")
                val = (text, ctx.guild.id)
                await ctx.send(f"{text}にアップデートしました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()





    @settings.command(description="退出時のチャンネルを設定します")
    async def remove_channel(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f"SELECT remove_channel_id FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO ServerSetting(guild_id,remove_channel_id) VALUES(?,?)")
                val = (ctx.guild.id, channel.id)
                await ctx.send(f"Channel has been set to {channel.mention}")
            elif result is not None:
                sql = ("UPDATE ServerSetting SET remove_channel_id = ? WHERE guild_id = ?")
                val = (channel.id, ctx.guild.id)
                await ctx.send(f"Channel has been updated to {channel.mention}")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")



    @settings.command()#button式
    async def menu(self, ctx):
        embed = discord.Embed(title="セッティングメニュー",color=self.bot.color)
        msg = await ctx.send(
            embed=embed,
            components=[
                [
                    Button(style=ButtonStyle.red, label="ログチャンネルを設定", emoji='🗨️'),
                    Button(style=ButtonStyle.green, label="ウェルカムチャンネルを設定", emoji='🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
                    Button(style=ButtonStyle.blue, label="ログチャンネルをリセット"),
                    Button(style=ButtonStyle.gray, label="ウェルカムチャンネルをリセット"),
                ],
            ],
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel

        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=30)
        except asyncio.exceptions.TimeoutError:
            tembed = discord.Embed(title="Timeout")
            await msg.edit(
                embed=tembed,
                components=[
                    Button(style=ButtonStyle.red, label="Timeout", disabled=True)
                ],
            )
            await asyncio.sleep(3)
            await msg.delete()
            return
        if res.component.label == "ログチャンネルを設定":
            if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                e = discord.Embed(title="logとして設定したいチャンネルidを送信してください",color = self.bot.color)
                await msg.edit(content=None, embed=e)
                message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                           in message.content.split()]
                await msg.delete()
                for channel in channel:
                    db = sqlite3.connect('main.sqlite')
                    cursor = db.cursor()
                    cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
                    result = cursor.fetchone()
                    if result is None:

                        sql = ("INSERT INTO ServerSetting(guild_id,log_channel) VALUES(?,?)")
                        val = (ctx.guild.id, channel.id)
                        e = discord.Embed(title="ログチャンネルをセットしました",color=self.bot.color)
                        e.add_field(name="取得できる内容", value="ユーザーの退出(入出)や役職の付与剥奪\nチャンネル(役職/メッセージの作成削除や設定変更等...")
                        e.add_field(name="該当チャンネル", value=channel.mention)
                        await ctx.send(embed=e)

                    elif result is not None:
                        sql = ("UPDATE ServerSetting SET log_channel = ? WHERE guild_id = ?")
                        val = (channel.id, ctx.guild.id)
                        e = discord.Embed(title="ログチャンネルをセットしました")
                        e.add_field(name="取得できる内容", value="ユーザーの退出(入出)や役職の付与剥奪\nチャンネル(役職/メッセージの作成削除や設定変更等...")
                        e.add_field(name="該当チャンネル", value=channel.mention)
                        await ctx.send(embed=e)

                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
            else:
                await ctx.send("権限がありません")

        elif res.component.label == "ウェルカムチャンネルを設定":
            if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                await ctx.send("welcome_channelとして設定したいチャンネルidを送信してください")
                message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                           in message.content.split()]
                await msg.delete()
                for channel in channel:
                    db = sqlite3.connect('main.sqlite')
                    cursor = db.cursor()
                    cursor.execute(f"SELECT welcome_channel_id FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
                    result = cursor.fetchone()
                    if result is None:
                        sql = ("INSERT INTO ServerSetting(guild_id,welcome_channel_id) VALUES(?,?)")
                        val = (ctx.guild.id, channel.id)
                        await ctx.send(f"{channel.mention}をウェルカムチャンネルとして設定しました")
                    elif result is not None:
                        sql = ("UPDATE ServerSetting SET welcome_channel_id = ? WHERE guild_id = ?")
                        val = (channel.id, ctx.guild.id)
                        await ctx.send(f"{channel.mention}をウェルカムチャンネルとして設定しました")
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()

        elif res.component.label == "ログチャンネルをリセット":
            if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                e = discord.Embed(title="設定されているlog_channelを入力してください\nlog_channelの確認方法は`y/settings list`で確認できます",color = self.bot.color)
                await msg.edit(content=None, embed=e)
                message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                           in message.content.split()]
                for channel in channel:
                    db = sqlite3.connect('main.sqlite')
                    cursor = db.cursor()

                    cursor.execute("DELETE FROM ServerSetting "
                                   "WHERE log_guild_id = ? AND log_channel  = ?",
                                   [int(ctx.guild.id), int(channel.id)])

                    await ctx.send(f"{channel.mention}を削除しました")
                    db.commit()
                    cursor.close()
                    db.close()
                else:
                    await ctx.send("権限がありません")

        elif res.component.label == "ウェルカムチャンネルをリセット":
            if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                e = discord.Embed(title="設定されているwelcome_channelを入力してください\nwelcome_channelの確認方法は`y/settings list`で確認できます",color = self.bot.color)
                await msg.edit(content=None, embed=e)
                message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                           in message.content.split()]
                for channel in channel:
                    db = sqlite3.connect('main.sqlite')
                    cursor = db.cursor()

                    cursor.execute("DELETE FROM ServerSetting "
                                   "WHERE guild_id = ? AND welcome_channel_id = ?",
                                   [int(ctx.guild.id), int(channel.id)])

                    await ctx.send(f"{channel.mention}を削除しました")
                    db.commit()
                    cursor.close()
                    db.close()
                else:
                    await ctx.send("権限がありません")


    @commands.Cog.listener()
    async def on_message(self, message):
        def _check(m):
            return (m.author == message.author
                    and len(m.mentions)
                    and (datetime.utcnow() - m.created_at).seconds < 60)

        if not message.author.bot:
            if len(list(filter(lambda m: _check(m), self.bot.cached_messages))) >= 3:
                await message.channel.send("Don't spam mentions!", delete_after=10)

    @commands.command(name='select-test')
    async def select_test(self, ctx):
        await ctx.send("Sever Setting",
                       components=
                       [Select(placeholder="settingsするものを選んでください",
                               options=[
                                   SelectOption(
                                       label="Set Log",
                                       value="logチャンネルを作成します",
                                       description="logチャンネルを作成します",
                                       emoji="😄"
                                   ),
                                   SelectOption(
                                       label="Set Welcome_channel",
                                       value="入出チャンネルを作成します",
                                       description="入出チャンネルを作成します",
                                       emoji="😄"
                                   ),
                                   SelectOption(
                                       label="Set Leave_channel",
                                       value="option3",
                                       description="退出チャンネルを作成します",
                                       emoji="😄"
                                   ),
                                   SelectOption(
                                       label="Reset log_channel",
                                       value="options4",
                                       description="ログチャンネルをリセットします"
                                   ),
                                   SelectOption(
                                       label="Reset Welcome_channel",
                                       value="options5",
                                       description="入出チャンネルをリセットします"
                                   ),
                                   SelectOption(
                                       label="Reset Leave_channel",
                                       value="options6",
                                       description="退出チャンネルをリセットします",
                                   ),
                               ])]
                       )
        e1 = discord.Embed(title="logをセット", description="下記の指示に沿ってセットしてください",color=self.bot.color)
        e2 = discord.Embed(title="入出チャンネルをセット", description="下記の指示に沿ってセットしてください",color=self.bot.color)
        e3 = discord.Embed(title="退出チャンネルをセット", description="下記の指示に沿ってセットしてください",color=self.bot.color)
        e4 = discord.Embed(title="logチャンネルをリセット",description="下記の指示に沿ってセットしてください",color=self.bot.color)
        e5 = discord.Embed(title="入出チャンネルをリセット",description="下記の指示に沿ってセットしてください",color=self.bot.color)
        e6 = discord.Embed(title="退出チャンネルをリセット", description="下記の指示に沿ってセットしてください", color=self.bot.color)

        while True:
            try:
                event = await self.bot.wait_for("select_option", check=None)

                label = event.component[0].label

                if label == "Set Log":
                    await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=True,  # we dont want to spam someone
                        embed=e1
                    )
                    if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                        e = discord.Embed(title="logとして設定したいチャンネルidを送信してください", color=self.bot.color)
                        msg = await ctx.send(embed=e)
                        message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                        channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                                   in message.content.split()]
                        await msg.delete()
                        for channel in channel:
                            db = sqlite3.connect('main.sqlite')
                            cursor = db.cursor()
                            cursor.execute(f"SELECT log_channel FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
                            result = cursor.fetchone()
                            if result is None:

                                sql = ("INSERT INTO ServerSetting(guild_id,log_channel) VALUES(?,?)")
                                val = (ctx.guild.id, channel.id)
                                e = discord.Embed(title="ログチャンネルをセットしました", color=self.bot.color)
                                e.add_field(name="取得できる内容", value="ユーザーの退出(入出)や役職の付与剥奪\nチャンネル(役職/メッセージの作成削除や設定変更等...")
                                e.add_field(name="該当チャンネル", value=channel.mention)
                                await ctx.send(embed=e)

                            elif result is not None:
                                sql = ("UPDATE ServerSetting SET log_channel = ? WHERE guild_id = ?")
                                val = (channel.id, ctx.guild.id)
                                e = discord.Embed(title="ログチャンネルをセットしました")
                                e.add_field(name="取得できる内容", value="ユーザーの退出(入出)や役職の付与剥奪\nチャンネル(役職/メッセージの作成削除や設定変更等...")
                                e.add_field(name="該当チャンネル", value=channel.mention)
                                await ctx.send(embed=e)

                            cursor.execute(sql, val)
                            db.commit()
                            cursor.close()
                            db.close()
                    else:
                        await ctx.send("権限がありません")


                elif label == "Set Welcome_channel":
                    await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=True,  # we dont want to spam someone
                        embed=e2
                    )
                    if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                        msg = await ctx.send("入出チャンネルとして設定したいチャンネルidを送信してください")
                        message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                        channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                                   in message.content.split()]
                        await msg.delete()
                        for channel in channel:
                            db = sqlite3.connect('main.sqlite')
                            cursor = db.cursor()
                            cursor.execute(
                                f"SELECT welcome_channel_id FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
                            result = cursor.fetchone()
                            if result is None:
                                sql = ("INSERT INTO ServerSetting(guild_id,welcome_channel_id) VALUES(?,?)")
                                val = (ctx.guild.id, channel.id)
                                await ctx.send(f"{channel.mention}を入出チャンネルとして設定しました")
                            elif result is not None:
                                sql = ("UPDATE ServerSetting SET welcome_channel_id = ? WHERE guild_id = ?")
                                val = (channel.id, ctx.guild.id)
                                await ctx.send(f"{channel.mention}を入出チャンネルとして設定しました")
                            cursor.execute(sql, val)
                            db.commit()
                            cursor.close()
                            db.close()

                elif label == "Set Leave_channel":
                    await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=False,  # we dont want to spam
                        embed=e3
                    )
                    if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                        msg = await ctx.send("退出チャンネルとして設定したいチャンネルidを送信してください")
                        message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                        channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                                   in message.content.split()]
                        await msg.delete()
                        for channel in channel:
                            db = sqlite3.connect('main.sqlite')
                            cursor = db.cursor()
                            cursor.execute(
                                f"SELECT remove_channel_id FROM ServerSetting WHERE guild_id = {ctx.guild.id}")
                            result = cursor.fetchone()
                            if result is None:
                                sql = ("INSERT INTO ServerSetting(guild_id,remove_channel_id) VALUES(?,?)")
                                val = (ctx.guild.id, channel.id)
                                await ctx.send(f"{channel.mention}を退出チャンネルとして設定しました")
                            elif result is not None:
                                sql = ("UPDATE ServerSetting SET remove_channel_id = ? WHERE guild_id = ?")
                                val = (channel.id, ctx.guild.id)
                                await ctx.send(f"{channel.mention}を退出チャンネルとして設定しました")
                            cursor.execute(sql, val)
                            db.commit()
                            cursor.close()
                            db.close()
                        else:
                            await ctx.send("権限がありません")

                elif label == "Reset log_channel":
                    await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=False,  # we dont want to spam
                        embed=e4
                    )
                    if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                        e = discord.Embed(
                            title="設定されているlog_channelを入力してください\nlog_channelの確認方法は`y/settings list`で確認できます",
                            color=self.bot.color)
                        msg = await ctx.send(embed=e)
                        message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                        channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                                   in message.content.split()]
                        for channel in channel:
                            db = sqlite3.connect('main.sqlite')
                            cursor = db.cursor()

                            cursor.execute("DELETE FROM ServerSetting "
                                           "WHERE log_guild_id = ? AND log_channel  = ?",
                                           [int(ctx.guild.id), int(channel.id)])
                            await msg.delete()
                            await ctx.send(f"{channel.mention}を削除しました")
                            db.commit()
                            cursor.close()
                            db.close()
                        else:
                            await ctx.send("権限がありません")

                elif label == "Reset Welcome_channel":
                    await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=False,
                        embed=e5
                    )
                    if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                        e = discord.Embed(
                            title="設定されている入出チャンネルのidを入力してください\nwelcome_channelの確認方法は`y/settings list`で確認できます",
                            color=self.bot.color)
                        msg = await ctx.send(embed=e)
                        message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                        channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                                   in message.content.split()]
                        for channel in channel:
                            db = sqlite3.connect('main.sqlite')
                            cursor = db.cursor()
                            cursor.execute("DELETE FROM ServerSetting "
                                           "WHERE guild_id = ? AND welcome_channel_id = ?",
                                           [int(ctx.guild.id), int(channel.id)])
                            await msg.delete()
                            await ctx.send(f"{channel.mention}を削除しました")
                            db.commit()
                            cursor.close()
                            db.close()
                    else:
                        await ctx.send("権限がありません")

                elif label == "Reset Leave_channel":
                    await event.respond(
                        type=InteractionType.ChannelMessageWithSource,
                        ephemeral=False,
                        embed=e6
                    )
                    if ctx.message.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
                        e = discord.Embed(
                            title="設定されている退出チャンネルのidを入力してください\nleave_channelの確認方法は`y/settings list`で確認できます",
                            color=self.bot.color)
                        msg = await ctx.send(embed=e)
                        message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
                        channel = [await commands.converter.TextChannelConverter().convert(ctx, logtext) for logtext
                                   in message.content.split()]

                        for channel in channel:
                            db = sqlite3.connect('main.sqlite')
                            cursor = db.cursor()

                            cursor.execute("DELETE FROM ServerSetting "
                                           "WHERE guild_id = ? AND remove_channel_id  = ?",
                                           [int(ctx.guild.id), int(channel.id)])

                            await msg.delete()

                            await ctx.send(f"{channel.mention}を削除しました")
                            db.commit()
                            cursor.close()
                            db.close()
                    else:
                        await ctx.send("権限がありません")


            except discord.NotFound:
                print("error.")  # s


    @settings.command(name='list')
    async def _list(self, ctx):
        import sqlite3
        conn = sqlite3.connect('main.sqlite')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM ServerSetting WHERE guild_id = ?', (ctx.guild.id,))
        data = cursor.fetchall()
        if not data:
            return await ctx.send('データが見つかりませんでした')
        settings = data[0]
        embed = discord.Embed(title='Server Settings')
        embed.add_field(name='ログチャンネル', value=self.bot.get_channel(int(settings[4])).mention if settings[4] else 'なし')
        embed.add_field(name='Welcomeチャンネル', value=self.bot.get_channel(int(settings[1])).mention if settings[1] else 'なし')
        await ctx.send(embed=embed)





    @settings.command(description="退出時のチャンネルをリセットします")
    async def remove_reset_channel(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.author.guild_permissions.manage_messages or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            cursor.execute("DELETE FROM ServerSetting "
                           "WHERE guild_id = ? AND remove_channel_id  = ?",
                           [int(ctx.guild.id), int(channel.id)])

            await ctx.send(f"{channel.mention}を削除しました")
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")

    @settings.command(description="ログチャンネルをリセットします")
    async def log_reset(self, ctx, channel: discord.TextChannel):
        """`チャンネルの管理`"""
        if ctx.author.guild_permissions.manage_channels or ctx.author.id == 478126443168006164:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()

            cursor.execute("DELETE FROM ServerSetting "
                           "WHERE log_guild_id = ? AND log_channel  = ?",
                           [int(ctx.guild.id), int(channel.id)])

            await ctx.send(f"{channel.mention}を削除しました")
            db.commit()
            cursor.close()
            db.close()
        else:
            await ctx.send("権限がありません")

    @commands.Cog.listener()
    async def on_reaction_add(self, payload):
        if payload.member.bot:
            return
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM reactrole WHERE guild_id = ?", (payload.guild_id,))
        data = cursor.fetchall()

        if not data:
            return
        else:
            for x in data:
                if x[2] == str(payload.emoji) and int(x[3]) == payload.message_id:
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x[1])
                    await payload.member.add_roles(role)

    @commands.Cog.listener()
    async def on_reaction_remove(self, payload):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM reactrole WHERE guild_id = ?", (payload.guild_id,))
        data = cursor.fetchall()

        if not data:
            return
        else:
            for x in data:
                if str(payload.emoji)[-1:] in x[2] and int(x[3]) == payload.message_id:
                    role = discord.utils.get(self.bot.get_guild(payload.guild_id).roles, id=x[1])
                    await self.bot.get_guild(payload.guild_id).get_member(payload.user_id).remove_roles(role)



def setup(bot):
    bot.add_cog(ServerSetting(bot))

