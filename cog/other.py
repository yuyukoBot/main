import asyncio
import codecs
import datetime
import time
from datetime import datetime

import discord
import discordlists
from bs4 import BeautifulSoup
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class everyone(commands.Cog):
    """
    誰でも使えるコマンドです
    """

    def __init__(self, bot):
        self.bot = bot
        self.api = discordlists.Client(self.bot)
        self.api.set_auth("bots.ondiscord.xyz", "dsag38_auth_token_fda6gs") # Set authorisation token for a bot list
        self.api.set_auth("discordbots.group", "qos56a_auth_token_gfd8g6") # Set authorisation token for a bot list
        self.api.start_loop()  # Posts the server count automatically every 30 minutes

    @cog_ext.cog_slash(name="test")
    async def _test(self, ctx: SlashContext):
        embed = discord.Embed(title="embed test")
        await ctx.send(content="test", embeds=[embed])

    @commands.command()
    async def post(self, ctx: commands.Context):
        """
        Manually posts guild count using discordlists.py (BotBlock)
        """
        try:
            result = await self.api.post_count()
        except Exception as e:
            await ctx.send("Request failed: `{}`".format(e))
            return

        await ctx.send("Successfully manually posted server count ({:,}) to {:,} lists."
                       "\nFailed to post server count to {:,} lists.".format(self.api.server_count,
                                                                             len(result["success"].keys()),
                                                                             len(result["failure"].keys())))

             
    @commands.command()
    async def get(self, ctx: commands.Context, bot_id: int = None):
        """
        Gets a bot using discordlists.py (BotBlock)
        """
        if bot_id is None:
            bot_id = self.bot.user.id
        try:
            result = (await self.api.get_bot_info(bot_id))[1]
        except Exception as e:
            await ctx.send("Request failed: `{}`".format(e))
            return

        await ctx.send("Bot: {}#{} ({})\nOwners: {}\nServer Count: {}".format(
            result['username'], result['discriminator'], result['id'],
            ", ".join(result['owners']) if result['owners'] else "Unknown",
            "{:,}".format(result['server_count']) if result['server_count'] else "Unknown"
        ))

    

    @commands.command(pass_context=True)
    async def translate(self, ctx, to_language, *, msg):
        """Translates words from one language to another. Do [p]help translate for more information.
        Usage:
        [p]translate <new language> <words> - Translate words from one language to another. Full language names must be used.
        The original language will be assumed automatically.
        """
        await ctx.message.delete()
        if to_language == "rot13":  # little easter egg
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name="Original", value=msg, inline=False)
            embed.add_field(name="ROT13", value=codecs.encode(msg, "rot_13"), inline=False)
            return await ctx.send("", embed=embed)
        async with self.bot.session.get(
                "https://gist.githubusercontent.com/astronautlevel2/93a19379bd52b351dbc6eef269efa0bc/raw/18d55123bc85e2ef8f54e09007489ceff9b3ba51/langs.json") as resp:
            lang_codes = await resp.json(content_type='text/plain')
        real_language = False
        to_language = to_language.lower()
        for entry in lang_codes:
            if to_language in lang_codes[entry]["name"].replace(";", "").replace(",", "").lower().split():
                language = lang_codes[entry]["name"].replace(";", "").replace(",", "").split()[0]
                to_language = entry
                real_language = True
        if real_language:
            async with self.bot.session.get("https://translate.google.com/m",
                                            params={"hl": to_language, "sl": "auto", "q": msg}) as resp:
                translate = await resp.text()
            result = str(translate).split('class="t0">')[1].split("</div>")[0]
            result = BeautifulSoup(result, "lxml").text
            embed = discord.Embed(color=discord.Color.blue())
            embed.add_field(name="Original", value=msg, inline=False)
            embed.add_field(name=language, value=result.replace("&amp;", "&"), inline=False)
            if result == msg:
                embed.add_field(name="Warning", value="This language may not be supported by Google Translate.")
            await ctx.send("", embed=embed)
        else:
            await ctx.send(self.bot.bot_prefix + "That's not a real language.")

    @commands.command()
    async def timer(self, ctx, seconds):
        try:
            secondint = int(seconds)
            if secondint > 1300:
                await ctx.send("300秒まで可能です")
                raise BaseException
            if secondint < 0 or secondint == 0:
                await ctx.send("I dont think im allowed to do negatives")
                raise BaseException
            message = await ctx.send("Timer: " + seconds)
            while True:
                secondint = secondint - 1
                if secondint == 0:
                    await message.edit(new_content=("Ended!"))
                    break
                await message.edit(new_content=("Timer: {0}".format(secondint)))
                await asyncio.sleep(1)
            await ctx.send(ctx.message.author.mention + " カウントダウン")
        except ValueError:
            await ctx.send("Must be a number!")

    @commands.command(name="say", aliases=["echo"], description="任意の文章を送信します。")
    async def say(self, ctx, *, arg):
        """`豆腐がしゃべります`"""
        await ctx.message.delete()
        if "<@" in arg or "@everyone" in arg or "@here" in arg:
            await ctx.send("```メンションはしないでください。```")
        else:
            await ctx.send(arg)


    @commands.command(name="invite", description="botの招待リンクを表示します")
    async def invite(self, ctx):
        """`誰でも`"""
        user = ctx.message.author
        embed = discord.Embed(title="invite-bot", color=0xb300ff)
        embed.set_thumbnail(
            url="https://images-ext-1.discordapp.net/external/p63_pSyVEDrhWnE2w87v2emUygjr2WA7AvD0m1mRaP8/%3Fsize%3D512/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
        embed.set_footer(text=user.name)
        embed.add_field(name="__**管理者権限**__",
                        value="https://discord.com/api/oauth2/authorize?client_id=757807145264611378&permissions=8&scope=bot")
        embed.add_field(name="__**Moderation機能**__",
                        value="https://discord.com/api/oauth2/authorize?client_id=757807145264611378&permissions=1544027255&scope=bot")
        embed.add_field(name="__**権限なし**__",
                        value="https://discord.com/api/oauth2/authorize?client_id=757807145264611378&permissions=0&scope=bot")
        await ctx.send(embed=embed)

    @commands.command(description="サポート鯖の情報です")
    async def official(self, ctx):
        """`誰でも`"""
        embed = discord.Embed(title="Yuyuko Support Server", url="https://discord.gg/xcwZYny",
                              description="幽々子のサポートサーバーです", color=0xb300ff)
        embed.set_thumbnail(
            url="https://images-ext-1.discordapp.net/external/p63_pSyVEDrhWnE2w87v2emUygjr2WA7AvD0m1mRaP8/%3Fsize%3D512/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
        embed.add_field(name="何かあればこちらへ", value="by creater", inline=True)
        embed.set_footer(text="幽々子")
        await ctx.send(embed=embed)



    @commands.command(name="time", description="現在時刻を表示するよ！")
    async def time_(self,ctx):
        import locale
        locale.setlocale(locale.LC_CTYPE, "English_United States.932")
        await ctx.send(datetime.datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒"))



def setup(bot):
    bot.add_cog(everyone(bot))