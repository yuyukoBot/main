import discord
import json
from discord.ext import commands
import sqlite3
import os
from discord_components import *
intents = discord.Intents.default()
intents.presences = True
intents.members = True

updateinfos = "・コマンド追加"

release = "0.2"
status = "Beta"
sss = "aaa"
intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.emojis = True

with open('./config.json', 'r') as cjson:
    config = json.load(cjson)
ver = "2.1"
token = config["TOKEN"]
prefix = config["prefix"]




bot = commands.Bot(command_prefix=prefix,activety=discord.Game(name="yuyuko"), intents=intents,help_command=None)
db=sqlite3.connect("main.db",detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
bot.db=db
bot.close_=bot.close
async def newclose():
    db.commit()
    db.close()
    await bot.close_()
def savedb():
    db.commit()
bot.close=newclose
bot.savedb=savedb
bot.cursor=db.cursor()
DiscordComponents(bot)

bot.load_extension('jishaku')
bot.load_extension('utils.error')


if __name__ == '__main__':
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")





@bot.event
async def on_command(ctx):
    e = discord.Embed(title="コマンド実行", description=f"実行分:`{ctx.message.clean_content}`")
    e.set_author(name=f"{ctx.author}({ctx.author.id})", icon_url=ctx.author.avatar_url_as(static_format="png"))
    e.add_field(name="実行サーバー", value=f"{ctx.guild.name}({ctx.guild.id})")
    e.add_field(name="実行チャンネル", value=ctx.channel.name)
    e.set_thumbnail(url=ctx.guild.icon_url)
    e.timestamp = ctx.message.created_at
    ch = bot.get_channel(797335889431756800)
    await ch.send(embed=e)
@bot.event
async def on_guild_join(guild):
    e = discord.Embed(title="サーバー加入")
    if guild.icon:
        e.set_thumbnail(url=guild.icon_url)
    e.add_field(name="サーバー名", value=f'`{guild.name}({guild.id})`')
    e.add_field(name="サーバーowner", value=guild.owner)
    e.add_field(name="AFKチャンネル", value=guild.afk_channel)
    bm = 0
    ubm = 0
    for m in guild.members:
        if m.bot:
            bm = bm + 1
        else:
            ubm = ubm + 1
    e.add_field(name="メンバー数",
                value=f"{len(guild.members)}(<:bot:798877222638845952>:{bm}/:busts_in_silhouette::{ubm})")
    e.add_field(name="チャンネル数",
                value=f'{("<:categorie:798883839124308008>")}:{len(guild.categories)}\n{(":speech_balloon:")}:{len(guild.text_channels)}\n{(":mega:")}:{len(guild.voice_channels)}')
    e.add_field(name="絵文字", value=len(guild.emojis))
    e.add_field(name="地域", value=str(guild.region))
    e.add_field(name="認証度", value=str(guild.verification_level))
    if guild.afk_channel:
        e.add_field(name="AFKチャンネル", value=f"{guild.afk_channel.name}({str(guild.afk_channel.id)})")
        e.add_field(name="AFKタイムアウト", value=str(guild.afk_timeout / 60))
    if guild.system_channel:
        e.add_field(name="システムチャンネル", value=f"{guild.system_channel}\n({str(guild.system_channel.id)})")
    try:
        e.add_field(name="welcome", value=guild.system_channel_flags.join_notifications)
        e.add_field(name="boost", value=guild.system_channel_flags.premium_subscriptions)
    except:
        pass
    ch = bot.get_channel(817642658599141417)
    await ch.send(embed=e)
    e1 = discord.Embed(title="幽々子の導入ありがとうございます",
                       description="詳しくは`y/help`でご確認ください\nこのbotは主に,logやmoderation,music,information等の機能があります", color=0x5d00ff)
    try:
        await guild.system_channel.send(embed=e1)
    except:
        for ch in guild.text_channels:
            try:
                await ch.send(embed=e1)
                return
            except:
                continue
@bot.command()
async def notice(ctx, ch: int=None):
    if ctx.author.guild_permissions.administrator or ctx.author.id == 478126443168006164:
        tchid = ch or ctx.channel.id
        tch = bot.get_channel(tchid)
        fch = bot.get_channel(757777897992880211)
        await fch.follow(destination=tch)
        await ctx.send("フォローが完了しました。")
    else:
        await ctx.send("権限がありません")
@bot.event
async def on_guild_remove(guild):
        e = discord.Embed(title="サーバー退出")
        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)
        e.add_field(name="サーバー名", value=f'`{guild.name}({guild.id})`')
        e.add_field(name="サーバーowner", value=guild.owner)
        e.add_field(name="AFKチャンネル", value=guild.afk_channel)
        bm = 0
        ubm = 0
        for m in guild.members:
            if m.bot:
                bm = bm + 1
            else:
                ubm = ubm + 1
        e.add_field(name="メンバー数",
                    value=f"{len(guild.members)}(<:bot:798877222638845952>:{bm}/:busts_in_silhouette::{ubm})")
        e.add_field(name="チャンネル数",
                    value=f'{("<:categorie:798883839124308008>")}:{len(guild.categories)}\n{(":speech_balloon:")}:{len(guild.text_channels)}\n{(":mega:")}:{len(guild.voice_channels)}')
        e.add_field(name="絵文字", value=len(guild.emojis))
        e.add_field(name="地域", value=str(guild.region))
        e.add_field(name="認証度", value=str(guild.verification_level))
        if guild.afk_channel:
            e.add_field(name="AFKチャンネル", value=f"{guild.afk_channel.name}({str(guild.afk_channel.id)})")
            e.add_field(name="AFKタイムアウト", value=str(guild.afk_timeout / 60))
        if guild.system_channel:
            e.add_field(name="システムチャンネル", value=f"{guild.system_channel}\n({str(guild.system_channel.id)})")
        try:
            e.add_field(name="welcome", value=guild.system_channel_flags.join_notifications)
            e.add_field(name="boost", value=guild.system_channel_flags.premium_subscriptions)
        except:
            pass
        ch = bot.get_channel(817642658599141417)
        await ch.send(embed=e)
@bot.event
async def on_ready():
    print("ログインに成功しました")
    await bot.change_presence(activity = discord.Game(name="起動しています…｜y/help"),status =discord.Status.idle)
    print(bot.user.name)
    print(bot.user.id)
    print("起動時の情報を送信しています… / Owner")
    channel = bot.get_channel(813379637228863509)
    e = discord.Embed(title="起動成功 - 詳細情報", description="起動処理が正常に終了しました。")
    e.add_field(name="バージョン情報", value=f"Ver:{ver}\nRelease:{release}\nStatus:{status}")
    e.add_field(name="更新情報", value=f"```\n{updateinfos}```")
    e.add_field(name="導入サーバー数", value=len(bot.guilds), inline=False)
    pingtime = bot.latency * 1000
    e.add_field(name="応答速度", value=pingtime)
    await channel.send(embed=e)
    print("最終処理を実行しています…")
    await bot.change_presence(activity=discord.Game(
        name=f"y/help｜Ver:{ver}｜Release:{release}｜{len(bot.guilds)}Guilds & {len(bot.users)}Users"),
                              status=discord.Status.online)
    print("Debug Console.")
    for allguild in bot.guilds:
        print(allguild)
    print("正常に起動しました。")


@bot.event
async def on_command_error(ctx, error):
    ch = 799505924280156192
    embed = discord.Embed(title="エラー情報", description="", color=0xf00)
    embed.add_field(name="エラー発生サーバー名", value=ctx.guild.name, inline=False)
    embed.add_field(name="エラー発生サーバーID", value=ctx.guild.id, inline=False)
    embed.add_field(name="エラー発生ユーザー名", value=ctx.author.name, inline=False)
    embed.add_field(name="エラー発生ユーザーID", value=ctx.author.id, inline=False)
    embed.add_field(name="エラー発生コマンド", value=ctx.message.content, inline=False)
    embed.add_field(name="発生エラー", value=error, inline=False)
    m = await bot.get_channel(ch).send(embed=embed)
    await ctx.send("エラーが発生しました")
bot.run(token)
