# -*- coding: utf-8 -*-

"""
jishaku.cog_base
~~~~~~~~~~~~~~~~~

The Jishaku cog base, which contains most of the actual functionality of Jishaku.

:copyright: (c) 2020 Devon (Gorialis) R
:license: MIT, see LICENSE for more details.

"""

import asyncio
import collections
import contextlib
import datetime
import inspect
import io
import itertools
import os
import os.path
import re
import sys
import time
import traceback
import typing

import aiohttp
import discord
from discord.ext import commands

from jishaku.codeblocks import Codeblock, codeblock_converter
from jishaku.exception_handling import ReplResponseReactor
from jishaku.flags import JISHAKU_RETAIN, SCOPE_PREFIX
from jishaku.functools import AsyncSender
from jishaku.models import copy_context_with
from jishaku.modules import ExtensionConverter
from jishaku.paginators import PaginatorInterface, WrappedFilePaginator, WrappedPaginator
from jishaku.repl import AsyncCodeExecutor, Scope, all_inspections, get_var_dict_from_ctx
from jishaku.shell import ShellReader
from jishaku.voice import BasicYouTubeDLSource, connected_check, playing_check, vc_check, youtube_dl

__all__ = (
    "owner",
)


CommandTask = collections.namedtuple("CommandTask", "index ctx task")


class owner(commands.Cog):  # pylint: disable=too-many-public-methods
    """
    The cog that includes Jishaku's Discord-facing default functionality.
    """

    load_time = datetime.datetime.now()

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._scope = Scope()
        self.retain = JISHAKU_RETAIN
        self.last_result = None
        self.start_time = datetime.datetime.now()
        self.tasks = collections.deque()
        self.task_count: int = 0

    @property
    def scope(self):
        """
        Gets a scope for use in REPL.

        If retention is on, this is the internal stored scope,
        otherwise it is always a new Scope.
        """

        if self.retain:
            return self._scope
        return Scope()

    @contextlib.contextmanager
    def submit(self, ctx: commands.Context):
        """
        A context-manager that submits the current task to jishaku's task list
        and removes it afterwards.

        Parameters
        -----------
        ctx: commands.Context
            A Context object used to derive information about this command task.
        """

        self.task_count += 1

        # 3.6 shim
        # As of current, pylint is unable to detect version_info checks to avoid linting for missing attributes.
        # As such, we're going to have to ignore such warnings explicitly, else they prevent CI from passing.
        # See https://github.com/PyCQA/pylint/labels/topic-control-flow
        if sys.version_info < (3, 7, 0):
            cmdtask = CommandTask(self.task_count, ctx, asyncio.Task.current_task())  # pylint: disable=no-member
        else:
            try:
                current_task = asyncio.current_task()  # pylint: disable=no-member
            except RuntimeError:
                # asyncio.current_task doesn't document that it can raise RuntimeError, but it does.
                # It propagates from asyncio.get_running_loop(), so it happens when there is no loop running.
                # It's unclear if this is a regression or an intentional change, since in 3.6,
                #  asyncio.Task.current_task() would have just returned None in this case.
                current_task = None

            cmdtask = CommandTask(self.task_count, ctx, current_task)

        self.tasks.append(cmdtask)

        try:
            yield cmdtask
        finally:
            if cmdtask in self.tasks:
                self.tasks.remove(cmdtask)

    async def cog_check(self, ctx: commands.Context):  # pylint: disable=invalid-overridden-method
        """
        Local check, makes all commands in this cog owner-only
        """

        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner("You must own this bot to use Jishaku.")
        return True

    @commands.command(name="source", aliases=["src"])
    async def source(self, ctx: commands.Context, *, command_name: str):
        """
        Displays the source code for a command.
        """

        command = self.bot.get_command(command_name)
        if not command:
            return await ctx.send(f"Couldn't find command `{command_name}`.")

        try:
            source_lines, _ = inspect.getsourcelines(command.callback)
        except (TypeError, OSError):
            return await ctx.send(f"Was unable to retrieve the source for `{command}` for some reason.")

        # getsourcelines for some reason returns WITH line endings
        source_lines = ''.join(source_lines).split('\n')

        paginator = WrappedPaginator(prefix='```py', suffix='```', max_size=1985)
        for line in source_lines:
            paginator.add_line(line)

        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)

    __cat_line_regex = re.compile(r"(?:\.\/+)?(.+?)(?:#L?(\d+)(?:\-L?(\d+))?)?$")

    @commands.is_owner()
    @commands.command(name="cat")
    async def cat(self, ctx: commands.Context, argument: str):
        """
        Read out a file, using syntax highlighting if detected.

        Lines and linespans are supported by adding '#L12' or '#L12-14' etc to the end of the filename.
        """

        match = self.__cat_line_regex.search(argument)

        if not match:  # should never happen
            return await ctx.send("Couldn't parse this input.")

        path = match.group(1)

        line_span = None

        if match.group(2):
            start = int(match.group(2))
            line_span = (start, int(match.group(3) or start))

        if not os.path.exists(path) or os.path.isdir(path):
            return await ctx.send(f"`{path}`: No file by that name.")

        size = os.path.getsize(path)

        if size <= 0:
            return await ctx.send(f"`{path}`: Cowardly refusing to read a file with no size stat"
                                  f" (it may be empty, endless or inaccessible).")

        if size > 50 * (1024 ** 2):
            return await ctx.send(f"`{path}`: Cowardly refusing to read a file >50MB.")

        try:
            with open(path, "rb") as file:
                paginator = WrappedFilePaginator(file, line_span=line_span, max_size=1985)
        except UnicodeDecodeError:
            return await ctx.send(f"`{path}`: Couldn't determine the encoding of this file.")
        except ValueError as exc:
            return await ctx.send(f"`{path}`: Couldn't read this file, {exc}")

        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)

    @commands.is_owner()
    @commands.command(name="curl")
    async def curl(self, ctx: commands.Context, url: str):
        """
        Download and display a text file from the internet.

        This command is similar to jsk cat, but accepts a URL.
        """

        # remove embed maskers if present
        url = url.lstrip("<").rstrip(">")

        async with ReplResponseReactor(ctx.message):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.read()
                    hints = (
                        response.content_type,
                        url
                    )
                    code = response.status

            if not data:
                return await ctx.send(f"HTTP response was empty (status code {code}).")

            try:
                paginator = WrappedFilePaginator(io.BytesIO(data), language_hints=hints, max_size=1985)
            except UnicodeDecodeError:
                return await ctx.send(f"Couldn't determine the encoding of the response. (status code {code})")
            except ValueError as exc:
                return await ctx.send(f"Couldn't read response (status code {code}), {exc}")

            interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
            await interface.send_to(ctx)

    @commands.is_owner()
    @commands.command(name="load")
    async def load(self, ctx: commands.Context, *extensions: ExtensionConverter):
        """
        Loads or reloads the given extension names.

        Reports any extensions that failed to load.
        """

        paginator = WrappedPaginator(prefix='', suffix='')

        for extension in itertools.chain(*extensions):
            method, icon = (
                (self.bot.reload_extension, "\N{CLOCKWISE RIGHTWARDS AND LEFTWARDS OPEN CIRCLE ARROWS}")
                if extension in self.bot.extensions else
                (self.bot.load_extension, "\N{INBOX TRAY}")
            )

            try:
                method(extension)
            except Exception as exc:  # pylint: disable=broad-except
                traceback_data = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__, 1))

                paginator.add_line(
                    f"{icon}\N{WARNING SIGN} `{extension}`\n```py\n{traceback_data}\n```",
                    empty=True
                )
            else:
                paginator.add_line(f"{icon} `{extension}`", empty=True)

        for page in paginator.pages:
            await ctx.send(page)



    @commands.is_owner()
    @commands.command(name="su")
    async def su(self, ctx: commands.Context, target: discord.User, *, command_string: str):
        """
        Run a command as someone else.

        This will try to resolve to a Member, but will use a User if it can't find one.
        """

        if ctx.guild:
            # Try to upgrade to a Member instance
            # This used to be done by a Union converter, but doing it like this makes
            #  the command more compatible with chaining, e.g. `jsk in .. jsk su ..`
            target_member = None

            with contextlib.suppress(discord.HTTPException):
                target_member = ctx.guild.get_member(target.id) or await ctx.guild.fetch_member(target.id)

            target = target_member or target

        alt_ctx = await copy_context_with(ctx, author=target, content=ctx.prefix + command_string)

        if alt_ctx.command is None:
            if alt_ctx.invoked_with is None:
                return await ctx.send('This bot has been hard-configured to ignore this user.')
            return await ctx.send(f'Command "{alt_ctx.invoked_with}" is not found')

        return await alt_ctx.command.invoke(alt_ctx)

    @commands.is_owner()
    @commands.command(name="py", aliases=["python"])
    async def python(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Direct evaluation of Python code.
        """

        arg_dict = get_var_dict_from_ctx(ctx, SCOPE_PREFIX)
        arg_dict["_"] = self.last_result

        scope = self.scope

        try:
            async with ReplResponseReactor(ctx.message):
                with self.submit(ctx):
                    executor = AsyncCodeExecutor(argument.content, scope, arg_dict=arg_dict)
                    async for send, result in AsyncSender(executor):
                        if result is None:
                            continue

                        self.last_result = result

                        if isinstance(result, discord.File):
                            send(await ctx.send(file=result))
                        elif isinstance(result, discord.Embed):
                            send(await ctx.send(embed=result))
                        elif isinstance(result, PaginatorInterface):
                            send(await result.send_to(ctx))
                        else:
                            if not isinstance(result, str):
                                # repr all non-strings
                                result = repr(result)

                            if len(result) > 2000:
                                # inconsistency here, results get wrapped in codeblocks when they are too large
                                #  but don't if they're not. probably not that bad, but noting for later review
                                paginator = WrappedPaginator(prefix='```py', suffix='```', max_size=1985)

                                paginator.add_line(result)

                                interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
                                send(await interface.send_to(ctx))
                            else:
                                if result.strip() == '':
                                    result = "\u200b"

                                send(await ctx.send(result.replace(self.bot.http.token, "[token omitted]")))
        finally:
            scope.clear_intersection(arg_dict)

    @commands.is_owner()
    @commands.command(name="py_inspect", aliases=["pyi", "python_inspect", "pythoninspect"])
    async def python_inspect(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Evaluation of Python code with inspect information.
        """

        arg_dict = get_var_dict_from_ctx(ctx, SCOPE_PREFIX)
        arg_dict["_"] = self.last_result

        scope = self.scope

        try:
            async with ReplResponseReactor(ctx.message):
                with self.submit(ctx):
                    executor = AsyncCodeExecutor(argument.content, scope, arg_dict=arg_dict)
                    async for send, result in AsyncSender(executor):
                        self.last_result = result

                        header = repr(result).replace("``", "`\u200b`").replace(self.bot.http.token, "[token omitted]")

                        if len(header) > 485:
                            header = header[0:482] + "..."

                        paginator = WrappedPaginator(prefix=f"```prolog\n=== {header} ===\n", max_size=1985)

                        for name, res in all_inspections(result):
                            paginator.add_line(f"{name:16.16} :: {res}")

                        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
                        send(await interface.send_to(ctx))
        finally:
            scope.clear_intersection(arg_dict)

    @commands.is_owner()
    @commands.command(name="shell")
    async def shell(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Executes statements in the system shell.

        This uses the system shell as defined in $SHELL, or `/bin/bash` otherwise.
        Execution can be cancelled by closing the paginator.
        """

        async with ReplResponseReactor(ctx.message):
            with self.submit(ctx):
                with ShellReader(argument.content) as reader:
                    prefix = "```" + reader.highlight

                    paginator = WrappedPaginator(prefix=prefix, max_size=1975)
                    paginator.add_line(f"{reader.ps1} {argument.content}\n")

                    interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
                    self.bot.loop.create_task(interface.send_to(ctx))

                    async for line in reader:
                        if interface.closed:
                            return
                        await interface.add_line(line)

                await interface.add_line(f"\n[status] Return code {reader.close_code}")

    @commands.is_owner()
    @commands.command(name="git")
    async def git(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Shortcut for 'jsk sh git'. Invokes the system shell.
        """

        return await ctx.invoke(self.shell, argument=Codeblock(argument.language, "git " + argument.content))

    @commands.is_owner()
    @commands.command(name="pip")
    async def pip(self, ctx: commands.Context, *, argument: codeblock_converter):
        """
        Shortcut for 'jsk sh pip'. Invokes the system shell.
        """

        return await ctx.invoke(self.shell, argument=Codeblock(argument.language, "pip " + argument.content))

    # Voice-related commands


def setup(bot):
    bot.add_cog(owner(bot))

