import asyncio
import codecs
import datetime
import time
import dns

import dns.resolver
import socket
from urllib.parse import unquote
import wikipedia
from discord.ext.commands import Bot
import io
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_components import DiscordComponents, Button
from datetime import datetime
from discord.ext import menus as dmenus
from util import Nullify
import discord
import discordlists
from bs4 import BeautifulSoup
from discord.ext import commands

from discord_slash import cog_ext, SlashContext
import aiohttp
from util.Error import ErrorMessage
from discord_components import DiscordComponents, Button, Select, SelectOption

time_window_milliseconds = 5000
max_msg_per_window = 5
author_msg_times = {}
class EmbedBuilderMenu(dmenus.Menu):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.embed = discord.Embed()

    async def send_initial_message(self, ctx, channel):
        return await channel.send("Welcome to the interactive embed builder menu. To get started, press the "
                                  "\N{INFORMATION SOURCE} button.")

    async def wait_for_message(self):
        def check(m):
            return m.author.id == self.ctx.author.id and m.channel.id == self.ctx.channel.id

        try:
            msg = await self.ctx.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await self.ctx.send("Timed out waiting for a message.")
            return
        return msg

    @dmenus.button("\N{MEMO}")
    async def set_description(self, payload):
        """Sets a description for the embed"""
        await self.message.edit(content="Send the message you want to add as a description")
        msg = await self.wait_for_message()
        self.embed.description = msg.content

    @dmenus.button("\N{LABEL}")
    async def set_title(self, payload):
        ctx = self.update_context(payload)
        command = self.bot.get_command('info')
        ctx.command = command

        await self.bot.invoke(ctx)

    @dmenus.button("\N{INFORMATION SOURCE}\ufe0f", position=dmenus.Last(3))
    async def info_page(self, payload) -> None:
        """shows you this message"""
        messages = []
        for emoji, button in self.buttons.items():
            messages.append(f'{str(emoji)} {button.action.__doc__}')

        embed = discord.Embed(title="Help", color=discord.Color.blurple())
        embed.clear_fields()
        embed.description = '\n'.join(messages)
        await self.message.edit(content=None, embed=embed)

    @dmenus.button("\N{CHEQUERED FLAG}")
    async def build(self, payload):
        """Sends the embed"""
        await self.ctx.send(embed=self.embed)
        self.stop()


class everyone(commands.Cog):
    """
    誰でも使えるコマンドです
    """

    def __init__(self, bot):
        self.bot = bot
        DiscordComponents(bot)
        self.api = discordlists.Client(self.bot)
        self.api.set_auth("bots.ondiscord.xyz", "dsag38_auth_token_fda6gs") # Set authorisation token for a bot list
        self.api.set_auth("discordbots.group", "qos56a_auth_token_gfd8g6") # Set authorisation token for a bot list
        self.api.start_loop()  # Posts the server count automatically every 30 minutes

    @commands.command()
    async def embedbuilder(self, ctx) -> None:
        """WIP embed builder command"""
        em = EmbedBuilderMenu()
        await em.start(ctx)

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

    @commands.command(name="select")
    async def test(self, ctx):
        await ctx.reply(  # Replying to message
            "Test select components",
            components=[  # List of components
                [
                    Select(  # Denotes a select box
                        placeholder="Please Choose A Car",  # Text displayed in the select (default box)
                        options=[
                            SelectOption(  # Creating an option
                                label="Ferrari",  # Name displayed on top
                                value="fer",  # Distinguishes in the interaction response
                                description="Italian Automaker",  # Extra info
                                emoji='🚙'
                            ),
                            SelectOption(  # Same as above
                                label="Bugatti",
                                value="bug",
                                description="French Automaker",
                                emoji='🚗'
                            ),
                            SelectOption(  # Same as above
                                label="Audi",
                                value="aud",
                                description="German Automaker",
                                emoji='🚘'
                            ),
                        ]
                    )
                ]
            ]
        )

        # Waiting for response...
        # Using try and except loop for the timeout
        try:
            # Wait_for statement
            ##Event is on_select_option
            interaction = await self.bot.wait_for(
                "select_option",  # Once someone selects and clicks out of the dropdown
                check=None,
                timeout=10.0  # 10 Second timeout
            )
            optValue = interaction.raw_data['d']['data']['values'][
                0]  # Their select returns the value of the option, fetching that

            # Library will add support for getting button label and so forth easily soon, this is a bit of dict stuff for now
            for value in interaction.raw_data['d']['message']['components'][0][
                'components']:  # Cycling through actionrows, if multiple
                for i in range(len(interaction.raw_data['d']['message']['components'][0]['components'][
                                       0])):  # For component in the first actionrow
                    if value['options'][i]['value'] == optValue:  # Checking if value matches select
                        name = value['options'][i]['label']  # Label of the selected option is here
                        break

                        # Responding with the option they chose
            await interaction.respond(
                type=4,  # New Message in channel
                ephemeral=False,  # Not hidden
                content=f"Thank you for using selects! \n> Your favourite car brand is **{name}**"
                # Telling them what they chose
            )
        except:
            # The disabling of select should come soon, rn its buggy so avoid it
            pass

    @commands.command(name="screenshot",aliases=["ss"],description="サイトのssを表示します")
    async def screenshot(self, ctx, url):
        """`誰でも`"""
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        embed = discord.Embed(title=f"Screenshot of {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://image.thum.io/get/width/1920/crop/675/maxAge/1/noanimate/{url}') as r:
                res = await r.read()
            embed.set_image(url="attachment://ss.png")
            embed.set_footer(
                text=f"{ctx.author} | TransHelper | {current_time} ")
            await ctx.send(file=discord.File(io.BytesIO(res), filename="ss.png"), embed=embed)

    @commands.command()
    async def button(self,ctx):

        await ctx.send(

            "Hello, World!",

            components=[

                Button(label="WOW button!")

            ]

        )

        interaction = await self.bot.wait_for("button_click", check=lambda i: i.component.label.startswith("WOW"))

        await interaction.respond(content="Button clicked!")

    @commands.command(pass_context=True,description="翻訳します")
    async def translate(self, ctx, to_language, *, msg):
        """`誰でも`"""
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

    @commands.command(
        brief="Frage DNS-Einträge ab",
        description="Frage bestimmte DNS-Einträge einer Domain ab.",
        aliases=["getdns"],
        help="",
        usage="<Domain> <Typ (CNAME, A, MX...)>"
    )
    async def dns(self, ctx, domain: str, typ: str = "A"):
        typ = typ.upper()
        try:
            result = dns.resolver.query(domain, typ)
            if typ == "A":
                await ctx.sendEmbed(
                    title="DNS-Info",
                    description=f"DNS-Einträge des Typs A für '{domain}'!",
                    inline=False,
                    fields=[
                        ("IP", ipval.to_text()) for ipval in result
                    ]
                )
            elif typ == "CNAME":
                await ctx.sendEmbed(
                    title="DNS-Info",
                    description=f"DNS-Einträge des Typs CNAME für '{domain}'!",
                    inline=False,
                    fields=[
                        ("CNAME Target", cnameval.target) for cnameval in result
                    ]
                )
            elif typ == "MX":
                await ctx.sendEmbed(
                    title="DNS-Info",
                    description=f"DNS-Einträge des Typs MX für '{domain}'!",
                    inline=False,
                    fields=[
                        ("MX Record", mxdata.exchange) for mxdata in result
                    ]
                )
            else:
                await ctx.sendEmbed(
                    title="DNS-Info",
                    description=f"DNS-Einträge des Typs '{typ}' für '{domain}'!",
                    inline=False,
                    fields=[
                        ("Eintrag", str(data)) for data in result
                    ]
                )
        except dns.resolver.NXDOMAIN:
            raise ErrorMessage(
                f"Die Domain '{domain}' konnte nicht gefunden werden!")
        except dns.resolver.NoAnswer:
            raise ErrorMessage(
                f"Für die Domain '{domain}' konnten keine DNS-Einträge des Typs '{typ}' gefunden werden!")
        except dns.rdatatype.UnknownRdatatype:
            raise ErrorMessage(
                f"Unbekannter DNS-Record Typ: {typ}")

    @commands.command(
        brief="Erhalte die IP einer Domain",
        description="Frage die IP-Adresse ab, welche hinter einer Domain steckt.",
        aliases=["ip"],
        help="",
        usage="<Domain>"
    )
    async def getip(self, ctx, domain: str):
        try:
            ip = socket.gethostbyname(domain)
            await ctx.sendEmbed(
                title="IP-Info",
                description=f"Die IP hinter '{domain}' lautet '{ip}'!",
            )
        except socket.gaierror:
            raise ErrorMessage(f"Die Domain '{domain}' konnte nicht gefunden werden!")

    @commands.command()
    async def timer(self, ctx, seconds):
        """`誰でも`"""
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
        """`誰でも`"""
        await ctx.message.delete()
        if "<@" in arg or "@everyone" in arg or "@here" in arg:
            await ctx.send("```メンションはしないでください。```")
        else:
            await ctx.send(arg)

        e = discord.Embed(title=arg)
        await ctx.send(embed=e)


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
        """`誰でも`"""
        import locale
        locale.setlocale(locale.LC_CTYPE, "English_United States.932")
        await ctx.send(datetime.datetime.now().strftime("%Y年%m月%d日 %H時%M分%S秒"))

    @commands.command(name="invite_bot",description="指定したbotの招待リンクを作成します")
    async def invite_bot(self, ctx, bot: discord.Member):
        """`誰でも`"""
        bot_invite = discord.Embed()
        bot_invite.set_thumbnail(url=bot.avatar_url)
        bot_invite.title = f"{bot.name} Invite"
        if bot.bot:
            bot_invite.description = (
                f"{bot.name} の招待リンクです"
            )
        else:
            bot_invite.description = "指定したidは間違っています"
        bot_invite.add_field(name="権限0",value=str(discord.utils.oauth_url(bot.id, discord.Permissions(0))))
        bot_invite.add_field(name="管理者権限",value=str(discord.utils.oauth_url(bot.id, discord.Permissions(8))))
        await ctx.send(embed=bot_invite)

    @commands.command(name="test_1")
    async def test_1(self,ctx):
        msg = await ctx.reply(  # Replying to message
            "Singular Selects Below.",
            components=[  # List of components
                [
                    Select(  # Denotes a select box
                        placeholder="Please Choose A Car",  # Text displayed in the select (default box)
                        options=[
                            SelectOption(  # Creating an option
                                label="Ferrari",  # Name displayed on top
                                value="fer",  # Distinguishes in the interaction response
                                description="Italian Automaker",  # Extra info
                            ),
                            SelectOption(  # Same as above
                                label="Bugatti", value="bug", description="French Automaker"
                            ),
                            SelectOption(  # Same as above
                                label="Audi", value="aud", description="German Automaker"
                            ),
                        ],
                    )
                ]
            ],
        )

        # Waiting for response...
        # Using try and except loop for the timeout
        try:
            # Wait_for statement
            ##Event is on_select_option
            interaction = await self.bot.wait_for(
                "select_option",  # Once someone selects and clicks out of the dropdown
                check=None,
                timeout=10.0,  # 10 Second timeout
            )
            name = interaction.component[0].label  # Getting label of select

            # Responding with the option they chose
            await interaction.respond(
                type=4,  # New Message in channel
                ephemeral=False,  # Not hidden
                content=f"Thank you for using selects! \n> Your favourite car brand is **{name}**",
                # Telling them what they chose
            )
        except asyncio.TimeoutError:
            # The disabling of select should come soon, rn its buggy so avoid it
            await msg.edit(
                components=[  # List of components
                    [
                        Select(  # Denotes a select box
                            placeholder="Please Choose A Car",  # Text displayed in the select (default box)
                            disabled=True,  # Disabling it
                            options=[
                                SelectOption(  # Creating an option
                                    label="Ferrari",  # Name displayed on top
                                    value="fer",  # Distinguishes in the interaction response
                                    description="Italian Automaker",  # Extra info
                                ),
                                SelectOption(  # Same as above
                                    label="Bugatti",
                                    value="bug",
                                    description="French Automaker",
                                ),
                                SelectOption(  # Same as above
                                    label="Audi",
                                    value="aud",
                                    description="German Automaker",
                                ),
                            ],
                        )
                    ]
                ]
            )



def setup(bot):
    bot.add_cog(everyone(bot))