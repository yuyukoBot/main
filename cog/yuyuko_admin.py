import textwrap
import discord
from discord import Intents
import typing
import colorsys
import os
import random
import traceback
import inspect
import sqlite3
import asyncio
import discord,fnmatch
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
from util import get_member_helpers,send_large_message
import os
import random
import traceback
from contextlib import redirect_stdout
import asyncio
from asyncio import sleep as _sleep

class AdminCog(commands.Cog, name="Admin"):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.stream = io.StringIO()
        self.channel = None


    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command()
    @commands.is_owner()
    async def guildv(self, ctx, gid: int, bl: bool = True):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        self.bot.cursor.execute(
            "UPDATE guilds SET verified = ? WHERE id = ?", (bl, gid))
        await ctx.send(f"サーバー`{self.bot.get_guild(gid)}`の認証状態を{str(bl)}にしました。")



    @commands.is_owner()
    @commands.command(pass_context=True)
    async def cloc(self, ctx):
        """`Bot運営`"""
        # Script pulled and edited from https://github.com/kyco/python-count-lines-of-code/blob/python3/cloc.py

        # Get our current working directory - should be the bot's home
        path = os.getcwd()

        # Set up some lists
        extensions = []
        code_count = []
        include = ['py', 'bat', 'sh', 'command']

        # Get the extensions - include our include list
        extensions = self.get_extensions(path, include)

        for run in extensions:
            extension = "*." + run
            temp = 0
            for root, dir, files in os.walk(path):
                for items in fnmatch.filter(files, extension):
                    value = root + "/" + items
                    temp += sum(+1 for line in open(value, 'rb'))
            code_count.append(temp)
            pass

        # Set up our output
        msg = 'Some poor soul took the time to sloppily write the following to bring me life:\n```\n'
        padTo = 0
        for idx, val in enumerate(code_count):
            # Find out which has the longest
            tempLen = len(str('{:,}'.format(code_count[idx])))
            if tempLen > padTo:
                padTo = tempLen
        for idx, val in enumerate(code_count):
            lineWord = 'lines'
            if code_count[idx] == 1:
                lineWord = 'line'
            # Setup a right-justified string padded with spaces
            numString = str('{:,}'.format(code_count[idx])).rjust(padTo, ' ')
            msg += numString + " " + lineWord + " of " + extensions[idx] + "\n"
            # msg += extensions[idx] + ": " + str(code_count[idx]) + ' ' + lineWord + '\n'
            # print(extensions[idx] + ": " + str(code_count[idx]))
            pass
        msg += '```'
        await ctx.send(msg)

    # Helper function to get extensions
    def get_extensions(self, path, excl):
        extensions = []
        for root, dir, files in os.walk(path):
            for items in fnmatch.filter(files, "*"):
                temp_extensions = items.rfind(".")
                ext = items[temp_extensions + 1:]
                if ext not in extensions:
                    if ext in excl:
                        extensions.append(ext)
                        pass
        return extensions

    @commands.command(name="reboot",description="BOTを再起動します")
    async def reboot(self,ctx):
        """`Bot運営`"""
        if ctx.message.author.id == 478126443168006164:
            e = discord.Embed(title="再起動", description="BOTを再起動するよ～！", color=ctx.author.color)
            await ctx.send(embed=e)
            os.system("python main.py")
        else:
            e = discord.Embed(title="実行エラー", description="あなたはこのコマンドを実行する権限を持っていません", color=ctx.author.color)
            await ctx.send(embed=e)

    @commands.command(name="send",description="指定たチャンネルにメッセージを送信します")
    @commands.is_owner()
    async def send(self, ctx, channel, *, message):
        """`Bot運営`"""

        if not ctx.message.channel_mention:
            return await ctx.send(
                f'<send> <チャンネル> <message> で使用できます')

        try:
            for channel in ctx.message.channel_mention:
                await channel.send(f'{message}')
                async with ctx.typing():
                    # do expensive stuff here
                    await asyncio.sleep(10)
        except Exception:
            ctx.send('Error when trying to send fam')





    @commands.command(name="unload", description="ファイルをアンロードします")
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """`Bot運営`"""
        try:
            self.bot.unload_extension(module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'`{module}をunloadしました`')

    @commands.is_owner()
    @commands.command(name='listextensions')
    async def list_extensions(self, ctx):
        """`Bot運営`"""
        extensions_dict = self.bot.extensions
        msg = '```css\n'

        extensions = []

        for b in extensions_dict:
            # print(b)
            extensions.append(b)

        for a in range(len(extensions)):
            msg += f'{a}: {extensions[a]}\n'

        msg += '```'
        await ctx.send(msg)


    @commands.command(pass_context=True, name='eval',description="コードを評価します")
    async def _eval(self, ctx, *, body: str):
        """`Bot運営`"""
        if ctx.author.id in [478126443168006164, 602680118519005184,691300045454180383]:

            env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'message': ctx.message,
                '_': self._last_result
            }

            env.update(globals())

            body = self.cleanup_code(body)
            stdout = io.StringIO()

            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

            try:
                exec(to_compile, env)
            except Exception as e:
                return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                value = stdout.getvalue()
                try:
                    await ctx.message.add_reaction('\u2705')
                except:
                    pass

                if ret is None:
                    if value:
                        await ctx.send(f'```py\n{value}\n```')
                else:
                    self._last_result = ret
                    await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command(description="BOTを再起動します")
    async def ru(self,ctx):
        """`Bot運営`"""

        if ctx.message.author.id == 478126443168006164:
            e = discord.Embed(title="再起動", description="BOTを再起動するよ～！", color=ctx.author.color)
            await ctx.send(embed=e)
            os.system("python bot.py")
        else:
            e = discord.Embed(title="実行エラー", description="あなたはこのコマンドを実行する権限を持っていません", color=ctx.author.color)
            await ctx.send(embed=e)

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def repl(self, ctx):
        """Launches an interactive REPL session."""
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            '_': None,
        }

        if ctx.channel.id in self.sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.')
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')

        def check(m):
            return m.author.id == ctx.author.id and \
                   m.channel.id == ctx.channel.id and \
                   m.content.startswith('`')

        while True:
            try:
                response = await self.bot.wait_for('message', check=check, timeout=10.0 * 60.0)
            except asyncio.TimeoutError:
                await ctx.send('Exiting REPL session.')
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self.sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = f'```py\n{value}{traceback.format_exc()}\n```'
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f'```py\n{value}{result}\n```'
                    variables['_'] = result
                elif value:
                    fmt = f'```py\n{value}\n```'

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await ctx.send('Content too big to be printed.')
                    else:
                        await ctx.send(fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await ctx.send(f'Unexpected error: `{e}`')

    @commands.group(name="system",description="システムコマンド")
    async def system(self,ctx):
        """`Bot運営のみ`"""
        return

    @system.command(description="コマンドプロンプトのコマンドを実行します")
    async def cmd(self,ctx, *, command):
        try:
            if ctx.author.id in [478126443168006164, 691300045454180383]:
                os.system(command)
                e = discord.Embed(title="Command", description="操作は正常に終了しました。")
                await ctx.send(embed=e)
            else:
                e2 = discord.Embed(title="Command", description="あなたはこのコマンドを実行する権限を持っていません。")
                await ctx.send(embed=e2)

        except Exception as error:
            e = discord.Embed(title="Command", description=f"Error\n```\n{error}\n```")
            await ctx.send(embed=e)

    @commands.is_owner()
    @system.command(name="changestatus",description="ステータスを変更します")
    async def changestatus(self, ctx, status: str):
        """`Bot運営`"""
        status = status.lower()
        if status == 'offline' or status == 'off' or status == 'invisible':
            discordStatus = discord.Status.invisible
        elif status == 'idle':
            discordStatus = discord.Status.idle
        elif status == 'dnd' or status == 'disturb':
            discordStatus = discord.Status.dnd
        else:
            discordStatus = discord.Status.online
        await self.bot.change_presence(status=discordStatus)
        await ctx.send(f'**:ok:** Ändere Status zu: **{discordStatus}**')

    @system.command(name="set_playing",description="再生状態を設定します。")
    @commands.is_owner()
    async def set_playing(self, ctx, *, game: str = None):
        """Set the playing status."""
        if game:
            await self.bot.change_presence(activity=discord.Game(game))
        ctx.delete()
        em = discord.Embed(color=0x00ff00)
        em.add_field(name="結果", value=f"{discord.Game(game)}に変わりました")
        await ctx.send(embed=em)

    @commands.is_owner()
    @system.command(name="announce", aliases=["ann"], description="アナウンス用")
    async def announce(self, ctx, *, message):
        """`Bot運営`"""

        await ctx.message.delete()
        ch = self.bot.get_channel(757777897992880211)
        em = discord.Embed(title="お知らせ", color=0x5d00ff)
        em.set_author(name="[y/]幽々子",
                      url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=512",
                      icon_url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=512")

        em.description = message
        try:
            await ch.send(embed=em)
            await ctx.send("アナウンスしました")
        except discord.Forbidden:
            await ctx.send("> 送信できません！\n　botに必要な権限が割り当てられているかどうかを確認してください。")
        except discord.HTTPException:
            await ctx.send("> 送信できません！\n　メッセージの送信に失敗しました。")

    @commands.is_owner()
    @system.command(name="news")
    async def news(self, ctx, *, message):
        """`Bot運営`"""

        await ctx.message.delete()
        em = discord.Embed(title="紹介", color=0x5d00ff)
        em.set_author(name="[y/]幽々子",
                      url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=512",
                      icon_url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=512")

        em.description = message
        await ctx.send(embed=em)

    @system.command(name="changenick",desceiption="ニックネームを設定します")
    @commands.is_owner()
    async def changenick(self, ctx, name=None):
        """`ニックネームの管理`"""
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        await ctx.message.guild.me.edit(nick=name)
        if name is None:
            await ctx.send("私のニックネームをデフォルトの名前に変更したよ。")
        else:
            await ctx.reply("私のニックネームを" + name + "に変更したよ。")

    @commands.is_owner()
    @commands.command()
    async def senddm(self,ctx, userid, title, desc):
        """`Bot運営`"""

        try:
            user = await commands.fetch_user(userid)
            e = discord.Embed(title=title, description=desc)
            e.set_author(name=ctx.author.name)
            await user.send(embed=e)

            c = discord.Embed(title="Senddm", description=f"{user.mention}にDMを送信しました。")
            await ctx.send(embed=c)

        except discord.NotFound:
            e = discord.Embed(title="Senddm", description="指定されたユーザーは存在しません")

        except discord.Forbidden:
            e = discord.Embed(title="Senddm", description="指定されたユーザーにDMを送信できませんでした。")
            await ctx.send(embed=e)

    @commands.is_owner()
    @system.command(hidden=True)
    async def listguild(self, ctx):
        '''Listet die aktuellen verbundenen Guilds auf (BOT OWNER ONLY)'''
        msg = '```js\n'
        msg += '{!s:19s} | {!s:>5s} | {} | {}\n'.format('ID', 'Member', 'Name', 'Owner')
        for guild in self.bot.guilds:
            msg += '{!s:19s} | {!s:>5s}| {} | {}\n'.format(guild.id, guild.member_count, guild.name, guild.owner)
        msg += '```'
        await ctx.reply(msg)

    @commands.is_owner()
    @system.command(name="shutdown", description="botを停止します")
    async def shutdown(self, ctx):
        """`Bot運営`"""


        e = discord.Embed(title="System - shutdown", description="処理中...", color=0x5d00ff)
        msg = await ctx.send(embed=e)

        try:
            e.description = None
            e.add_field(name="成功", value="Botを停止するよ！")

            await msg.edit(embed=e)
            await self.bot.change_presence(activity=discord.Game(name=f'Disabling YuyukoBot {self} Please Wait...'))
            await asyncio.sleep(5)

            await self.bot.close()
            return
        except Exception as er:
            e.description = None
            e.add_field(name="エラー", value=f"py\n{er}\n")
            print(f"[Error] {traceback.format_exc(3)}")
            await msg.edit(embed=e)



    @commands.command()
    @commands.cooldown(1, 60, commands.cooldowns.BucketType.channel)
    async def archive(self, ctx, *limit: int):
        """`Bot運営`"""

        if not limit:
            limit = 10
        else:
            limit = limit[0]
        logFile = f'{ctx.channel}.log'
        counter = 0
        with open(logFile, 'w', encoding='UTF-8') as f:
            f.write(
                f'Archivierte Nachrichten vom Channel: {ctx.channel} am {ctx.message.created_at.strftime("%d.%m.%Y %H:%M:%S")}\n')
            async for message in ctx.channel.history(limit=limit, before=ctx.message):
                try:
                    attachment = '[Angehängte Datei: {}]'.format(message.attachments[0].url)
                except IndexError:
                    attachment = ''
                f.write(
                    '{} {!s:20s}: {} {}\r\n'.format(message.created_at.strftime('%d.%m.%Y %H:%M:%S'), message.author,
                                                    message.clean_content, attachment))
                counter += 1
        msg = f':ok: {counter} Nachrichten wurden archiviert!'
        f = discord.File(logFile)
        await ctx.send(file=f, content=msg)
        os.remove(logFile)



def setup(bot):
    bot.add_cog(AdminCog(bot))
