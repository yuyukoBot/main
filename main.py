import discord

import json
from typing import Union
import logging
import textwrap

import asyncio
import random
import datetime
import DiscordUtils
import asyncpg
from discord.ext import commands
import utils.json_loader
updateinfos = "・コマンド追加"
release = "0.2"
status = "Beta"
from discord_slash import SlashCommand, SlashContext

intents = discord.Intents.default()
intents.members = True

with open('./config.json', 'r') as cjson:
    config = json.load(cjson)
database = config["database"]
user = config["user"]
password = config["password"]

async def main():
    # Establish a connection to an existing database named "test"
    # as a "postgres" user.
    conn = await asyncpg.connect(database=database ,user=user, password=password)


    # Insert a record into the created table.
    await conn.execute('''
        INSERT INTO users(name, dob) VALUES($1, $2)
    ''', 'Bob', datetime.date(1984, 3, 1))

    # Select a row from the table.
    row = await conn.fetchrow(
        'SELECT * FROM users WHERE name = $1', 'Bob')
    # *row* now contains
    # asyncpg.Record(id=1, name='Bob', dob=datetime.date(1984, 3, 1))

    # Close the connection.
    await conn.close()

asyncio.get_event_loop().run_until_complete(main())




ver = "2.1"


token = config["TOKEN"]
prefix = config["prefix"]
bot = commands.Bot(command_prefix=prefix,activety=discord.Game(name="yuyuko"), intents=intents,help_command=None)
slash = SlashCommand(bot, override_type = True)
bot.load_extension('jishaku')
bot.load_extension('cog.info')
bot.load_extension('cog.admin')
bot.load_extension('cog.report')
bot.load_extension('cog.giveaway')
bot.load_extension('cog.other')
bot.load_extension('cog.moderation')
bot.load_extension('cog.fun')
bot.load_extension('cog.monitor')
bot.load_extension('cog.setting')
bot.load_extension('cog.music')

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
async def on_ready():
    print("ログインに成功しました")
    await bot.change_presence(activity = discord.Game(name="起動しています…｜y/help"),status =discord.Status.idle)
    print(bot.user.name)
    print(bot.user.id)

    print("起動時の情報を送信しています… / Owner")
    channel = bot.get_channel(809946025090351154)
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





bot.remove_command('help')
@bot.command()
async def help(ctx):
    e1 = discord.Embed(title="Helpメニュー", description="`y/help <コマンド>`で確認できます\n```接頭辞:y/```", color=0x5d00ff).add_field(
        name="`幽々子ログ`というチャンネルを使うと自動でログチャンネルになります`", value="Page 1")
    e1.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/svQAPh7v9BBNiUgs3Fx4e27C1yhQ1KMp5h1KOhkKH3U/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
    e1.add_field(name="導入はこちらから",
                 value="https://discord.com/oauth2/authorize?client_id=757807145264611378&guild_id=757773097758883880&scope=bot")
    e2 = discord.Embed(title="<:outline_search_black_18dp:809104619103322165>information<:outline_search_black_18dp:809104619103322165>", color=0x5d00ff).add_field(name="Example", value="Page 2")
    e2.add_field(name="**userinfo <user>**", value="ユーザーの情報を表示します", inline=False)
    e2.add_field(name="**user <user>**", value="外部ユーザーの情報を表示します", inline=False)
    e2.add_field(name="**serverinfo <id>**", value="サーバーの情報を表示します", inline=False)
    e2.add_field(name="**server <サーバー名>**",value="サーバー名でも調べられます",inline=False)
    e2.add_field(name="**roleinfo <role>**", value="役職の情報を表示します", inline=False)
    e2.add_field(name="**channelinfo <channel>**", value="チャンネルの情報を表示します", inline=False)
    e2.add_field(name="**messageinfo <message>**", value="メッセージの情報を表示します", inline=False)
    e2.add_field(name="**avatar <user>**", value="ユーザーのアバターの情報を表示します", inline=False)
    e2.add_field(name="**emojiinfo <絵文字>**", value="絵文字の情報を表示します")
    e2.add_field(name="**messagehistory <数字>**",value="指定した分のメッセージの履歴を表示します")
    e3 = discord.Embed(title="<:outline_settings_black_18dp:809104587482988564>Moderation<:outline_settings_black_18dp:809104587482988564>", color=0x5d00ff).add_field(name="モデレーション機能です", value="Page 3",inline=True)
    e3.add_field(name="**kick <user> <reason>**", value="ユーザーをサーバーからkickします", inline=True)
    e3.add_field(name="**ban <user> <reason>**", value="ユーザーをサーバーからbanします", inline=True)
    e3.add_field(name="**unban <user>**", value="BANされたユーザーをban解除します", inline=True)
    e3.add_field(name="**hackban <user> <reason>**", value="ユーザーをhackbanします", inline=True)
    e3.add_field(name="**baninfo <user>**", value="banされたユーザーのban情報を表示します", inline=True)
    e3.add_field(name="**banlist**", value="banされたユーザー一覧を表示します", inline=True)
    e3.add_field(name="**poll <質問内容>**", value="アンケートを取れます", inline=True)
    e3.add_field(name="**addrole <user> <役職>**", value="ユーザーに役職を付与します", inline=True)
    e3.add_field(name="**removerole <user> <役職>**", value="ユーザーの役職を剥奪します", inline=True)
    e3.add_field(name="**mute <user> <秒数>**", value="ユーザーを指定した秒数muteします", inline=True)
    e3.add_field(name="**unmute <muteされたuser>**", value="muteを解除します", inline=True)
    e3.add_field(name="**purge <数字>**", value="指定された文字数分文章を消します")
    e4 = discord.Embed(title="everyone", description="誰でも使えます", colro=0x5d00ff)
    e4.add_field(name="**timer <秒数>**", value="タイマー機能です")
    e4.add_field(name="**invite**", value="招待リンクを表示します")
    e4.add_field(name="**official**", value="サポート鯖のリンクを表示します")
    e4.add_field(name="**ping**", value="ネットの速さを知れます")
    e4.add_field(name="**say <内容>**", value="幽々子に言いたいことを言わせます")
    e5 = discord.Embed(title="admin", description="page4", color=0x5d00ff)
    e5.add_field(name="**load/unload/reload <extension名>**", value="ファイルをロード/アンロード/リロードします",
                 inline=False)
    e5.add_field(name="**eval <コード>**", value="コードを評価します")
    e4.add_field(name="**changestatus <status>**", value="幽々子のステータスを変えます")
    e5.add_field(name="**changenick <名前>**", value="ユーザーのニックネームを変えます")
    e5.add_field(name="**set_playing <game名>**", value="幽々子のplaying statuを変えます")
    e5.add_field(name="**announce <内容>**", value="運営がアナウンスをします")
    e5.add_field(name="**dm <user> <内容>**", value="指定したユーザーにDMを送ります")
    e5.add_field(name="**servers**", value="botが入ってるサーバー一覧を表示します")
    e5.add_field(name="**system_shutdown**", value="botを停止します")
    e5.add_field(name="**log <数>**", value="指定された数分のメッセージを保存します")
    e5.add_field(name="**cmd <command>**",value="コマンドプロント")
    e6 = discord.Embed(title="fun", descriotion="お遊び機能です", color=0x5d00ff)
    e6.add_field(name="**password**", value="DMに暗号文を表示します")
    e6.add_field(name="**slot**", value="スロットをします")
    e7 = discord.Embed(title="report", description="何かあれば", color=0x5d00ff)
    e7.add_field(name="**request <要望> <理由>**", value="リクエスト随時受付中です")
    e7.add_field(name="**feedback <内容>**", value="フィートバックを送ります")
    e8 = discord.Embed(title="setting", description="logなどのsetting", color=0x5d00ff)
    e8.add_field(name="**log_setting**",value="ログチャンネルを作成します")
    e8.add_field(name="**new(delete) channnel <role> <チャンネル名>**",value="チャンネルを作成(削除)します")
    e8.add_field(name="**new(delete) category <role> <チャンネル名>**",value="カテゴリーを作成(削除)します")
    e8.add_field(name="**allrole(roleallremove)**",value="指定した役職を全メンバーに付与（剥奪)します")
    e8.add_field(name="**rolecreate(roledelete) <名前>**",value="役職を追加(消去)します")


    e2.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/svQAPh7v9BBNiUgs3Fx4e27C1yhQ1KMp5h1KOhkKH3U/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
    e3.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/svQAPh7v9BBNiUgs3Fx4e27C1yhQ1KMp5h1KOhkKH3U/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
    e4.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/svQAPh7v9BBNiUgs3Fx4e27C1yhQ1KMp5h1KOhkKH3U/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
    e5.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/svQAPh7v9BBNiUgs3Fx4e27C1yhQ1KMp5h1KOhkKH3U/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
    e6.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/svQAPh7v9BBNiUgs3Fx4e27C1yhQ1KMp5h1KOhkKH3U/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")
    e7.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/svQAPh7v9BBNiUgs3Fx4e27C1yhQ1KMp5h1KOhkKH3U/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")

    e8.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/svQAPh7v9BBNiUgs3Fx4e27C1yhQ1KMp5h1KOhkKH3U/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png")

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
    paginator.add_reaction('<:outline_fast_rewind_black_24dp:809040685881229373>', "first")
    paginator.add_reaction('<:arrowleftbox:809036770070233088>', "back")
    paginator.add_reaction('<:lockopen:809045312952991755>', "lock")
    paginator.add_reaction('<:arrowrightbox1:809038120678326273>', "next")
    paginator.add_reaction('<:outline_fast_forward_black_24dp:809040782358347778>', "last")
    embeds = [e1, e2, e3, e4, e5, e6, e7,e8]
    await paginator.run(embeds)



bot.run(token)