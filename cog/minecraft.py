
import discord
from discord.ext import commands
import sqlite3
import configparser
import os
import json
import pickle
from mojang import MojangAPI
import datetime
from mcstatus import MinecraftServer


def get_skin(mcid):
    "Get skin images"
    uuid=MojangAPI.get_uuid(str(mcid))
    if not uuid:
        return "404"
    else:
        try:
            profile = MojangAPI.get_profile(uuid)
            url=profile.skin_url
            return url
        except:
            return "API error"


class minecraft(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def register(self,ctx,*,mcid:str):
        status = get_skin(mcid)
        if not status == "404":
            self.bot.db.execute("INSERT INTO userdb(user_id,mcid) VALUES(?,?)", (ctx.author.id, mcid))
            embed = discord.Embed(title="登録完了", description="MCIDの登録が完了しました。")
            await ctx.send(embed=embed)
        else:
            await ctx.send("MCIDが確認できませんでした。MCIDは合っていますか?")

    @commands.command()
    async def change(self,ctx,*,mcid:str):
        status = get_skin(mcid)
        if not status == "404":
            SELECT = "SELECT mcid FROM userdb WHERE user_id = ?"
            has_entry = self.bot.db.execute(SELECT, (ctx.author.id,)).fetchone()
            if not has_entry == None:
                UPDATE = "UPDATE userdb SET mcid = ? WHERE user_id = ?"
                self.bot.db.execute(UPDATE, (mcid, ctx.author.id))
                embed = discord.Embed(title="変更完了", description="MCIDの変更が完了しました。")
                await ctx.send(embed=embed)
            else:
                await ctx.send("MCIDが登録されていません。`to:register [MCID]` で登録できます。")
        else:
            await ctx.send("MCIDが確認できませんでした。MCIDは合っていますか?")



def setup(bot):
    bot.add_cog(minecraft(bot))