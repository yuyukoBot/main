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
    async def color(self, ctx, color='0x000000'):
        print(f'{ctx.message.author.name}({ctx.message.guild.name})_' +
              ctx.message.content)
        self.bot.cursor.execute(
            "UPDATE profiles SET color = ? WHERE id = ?", (int(color, 16), ctx.author.id))
        await ctx.send("テスト")

    @profile.command(description="指定したチャンネルにウェルカムメッセージを設定します")
    async def nick(self, ctx, nick):
        """`メッセージの管理`"""
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT nick FROM profiles WHERE user_id = {ctx.author.id}")
        result = cursor.fetchone()
        if result is None:
            sql = ("INSERT INTO profiles(user_id, nick) VALUES(?,?)")
            val = (ctx.author.id, nick)
            await ctx.send(f"{nick}にセットしました")
        elif result is not None:
            sql = ("UPDATE profiles SET nick = ? WHERE user_id = ?")
            val = (nick, ctx.author.id)
            await ctx.send(f"{nick}にアップデートしました")
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @profile.command()
    async def user(self,ctx, member: discord.Member=None):
        member = member or ctx.author.id

        self.bot.cursor.execute("select * from profiles where user_id=?", (member))
        nick  = self.bot.cursor.fetchone()
        e = discord.Embed(title="プロフィール")
        e.add_field(name="nick", value=nick["nick"])

        await ctx.send(embed=e)




def setup(bot):
    bot.add_cog(profile(bot))