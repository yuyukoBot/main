import asyncio

import discord
from discord.ext.buttons import Paginator
import discord, re, collections, random, emoji, contextlib, typing
from discord.ext import commands

class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content


def getEmbed(ti, desc, color=int("0x61edff", 16), *optiontext):
    e = discord.Embed(title=ti, description=desc, color=color)
    nmb = -2
    while len(optiontext) >= nmb:
        try:
            nmb = nmb + 2
            e.add_field(name=optiontext[nmb], value=optiontext[nmb+1])
        except IndexError:
            pass
    return e


class BetterUserconverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            user = await commands.UserConverter().convert(ctx, argument)
        except commands.UserNotFound:
            user = None
        if not user and ctx.guild:
            user = ctx.guild.get_member_named(argument)

        if user == None:
            role = None

            with contextlib.suppress(commands.RoleNotFound, commands.NoPrivateMessage):
                role = await commands.RoleConverter().convert(ctx, argument)

            if role:
                if role.is_bot_managed():
                    user = role.tags.bot_id
                    user = ctx.bot.get_user(user) or await ctx.bot.fetch_user(user)

        if user == None:
            tag = re.match(r"#?(\d{4})", argument)
            if tag:
                test = discord.utils.get(ctx.bot.users, discriminator=tag.group(1))
                user = test or ctx.author
        return user

