import discord
from discord.ext import commands
import asyncio
import sqlite3

class profile(commands.Cog):
    def __init__(self,bot):
        self.bot = bot


    @commands.group()
    async def profile(self,ctx):
        return

    @profile.command()
    async def nick(self,ctx,nick):
        if 1 < len(nick) < 29:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(
                "SELECT nick FROM profiles WHERE id = ?", (nick, ctx.author.id))
            result = cursor.fetchone()
            if result is None:
                sql = ("INSERT INTO profils(nick) VALUES(?,?)")
                val = (nick, ctx.author.id)
                await ctx.send("ニックネームを設定しました")
            elif result is not None:
                sql = ("UPDATE profiles SET nick = ? WHERE id = ?", (nick, ctx.author.id))
                val = (nick, ctx.author.id)
                await ctx.send("アップデートしました")
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()


        else:
            await ctx.send("名前の長さは2文字以上28文字以下にしてください。")

    @profile.command()
    async def color(self, ctx, color='0x000000'):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        self.bot.cursor.execute(
            "UPDATE profiles SET color = ? WHERE id = ?", (int(color, 16), ctx.author.id))
        await ctx.send("テスト")

    @profile.command()
    async def user(self,ctx, member: discord.Member=None):
        if member is None:
            cid = ctx.author.id
        else:
            cid = ctx.author.id
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute("select * from profiles where id=?", (ctx.author.id,))
        upf = cursor.fetchone()
        e = discord.Embed(title="プロフィール")
        e.add_field(name="nick", value=upf["nick"])
        e.add_field(name="color", value=str(upf["color"]))
        await ctx.send(embed=e)




def setup(bot):
    bot.add_cog(profile(bot))