import asyncio

import discord
from discord.ext.buttons import Paginator


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

