import discord
from asyncio import sleep

import json
from typing import Union
import logging
import textwrap
from datetime import time
import datetime
import asyncio
import random
from discord.ext import commands


from logging import DEBUG, getLogger
logger = getLogger(__name__)
class log(commands.Cog):
    TIMEOUT_TIME = 30.0

    def __init__(self,bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_channel_create(self,channel):
        e = discord.Embed(title="チャンネル作成", timestamp=channel.created_at, color=0x5d00ff)
        e.add_field(name="チャンネル名", value=channel.mention)
        channel = discord.utils.get(channel.guild.channels, name="幽々子ログ")
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_ban(self,g, user):
        guild = commands.get_guild(g.id)
        bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        e = discord.Embed(title="ユーザーのban", color=0x5d00ff)
        e.add_field(name="ユーザー名", value=str(user))
        e.add_field(name="実行者", value=str(bl[0].user))
        channel = discord.utils.get(commands.get.channels, name="幽々子ログ")
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_invite_create(self,invite):
        e = discord.Embed(title="サーバー招待の作成", color=0x5d00ff)
        e.add_field(name="作成ユーザー", value=str(invite.inviter))
        e.add_field(name="使用可能回数", value=str(invite.max_uses))
        e.add_field(name="使用可能時間", value=str(invite.max_age))
        e.add_field(name="チャンネル", value=str(invite.channel.mention))
        e.add_field(name="コード", value=str(invite.code))
        channel = discord.utils.get(invite.guild.channels, name="幽々子ログ")
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_user_update(self,before, after):
        if before.name != after.name:
            e = discord.Embed(title="ニックネーム", color=0x5d00ff, timestamp=datetime.utcnow())
            fields = [("Before", before.name, False), ("After", after.name, False)]

            for name, value, inline in fields:
                e.add_field(name=name, value=value, inline=inline)

            channel = discord.utils.get(before.get_channels, name="幽々子ログ")
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        if not message.author.bot:
            e = discord.Embed(title="メッセージ削除", color=0x5d00ff)
            e.add_field(name="メッセージ", value=f'```{message.content}```', inline=False)
            e.add_field(name="メッセージ送信者", value=message.author.mention)
            e.add_field(name="メッセージチャンネル", value=message.channel.mention)
            e.add_field(name="メッセージのid", value=message.id)

            channel = discord.utils.get(message.guild.channels, name="幽々子ログ")
            await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        print("1")
        if before.name != after.name:
            embed = discord.Embed(title="役職の名前が変わりました", color=0x5d00ff)


            embed.add_field(name="名前", value=f'{after.name}({after.id})')
            embed.add_field(name="位置", value=after.position)
            if bool(after.hoist):
                embed.add_field(name="個別表示ですか", value="はい")
            else:
                embed.add_field(name="個別表示ですか", value="いいえ")

            if bool(after.mentionable):
                embed.add_field(name="メンション可能", value="はい")
            else:
                embed.add_field(name="メンション可能", value="いいえ")
            channel = discord.utils.get(before.guild.channels, name="幽々子ログ")
            await channel.send(embed=embed)

        if before.color != after.color:
            e = discord.Embed(title="役職の色が変わりました", color=0x5d00ff)
            e.add_field(name="id", value=after.id)
            e.add_field(name="名前", value=f'{after.name}({after.id})')
            e.add_field(name="位置", value=after.position)
            if bool(after.hoist):
                e.add_field(name="個別表示ですか", value="はい")
            else:
                e.add_field(name="個別表示ですか", value="いいえ")

            if bool(after.mentionable):
                e.add_field(name="メンション可能", value="はい")
            else:
                e.add_field(name="メンション可能", value="いいえ")
            channel = discord.utils.get(before.guild.channels, name="幽々子ログ")
            await channel.send(embed=e)

        if before.hoist != after.hoist:
            e1 = discord.Embed(title="役職を個別表示(非表示)にしました", color=0x5d00ff)

            e1.add_field(name="設定前", value=f'`{before.hoist}`')
            e1.add_field(name="設定後", value=f'`{after.hoist}`')
            e1.add_field(name="id", value=after.id)
            e1.add_field(name="名前", value=f'{after.name}({after.id})')
            e1.add_field(name="位置", value=after.position)
            if bool(after.hoist):
                e1.add_field(name="個別表示ですか", value="はい")
            else:
                e1.add_field(name="個別表示ですか", value="いいえ")

            if bool(after.mentionable):
                e1.add_field(name="メンション可能", value="はい")
            else:
                e1.add_field(name="メンション可能", value="いいえ")

            channel = discord.utils.get(before.guild.channels, name="幽々子ログ")
            await channel.send(embed=e1)

        if before.mentionable != after.mentionable:
            e2 = discord.Embed(title="役職をメンション可能(不可能)にしました", color=0x5d00ff)

            e2.add_field(name="設定前", value=f'`{before.mentionable}`')
            e2.add_field(name="設定後", value=f'`{after.mentionable}`')
            e2.add_field(name="id", value=after.id)
            e2.add_field(name="名前", value=f'{after.name}({after.id})')
            e2.add_field(name="位置", value=after.position)
            if bool(after.hoist):
                e2.add_field(name="個別表示ですか", value="はい")
            else:
                e2.add_field(name="個別表示ですか", value="いいえ")

            if bool(after.mentionable):
                e2.add_field(name="メンション可能", value="はい")
            else:
                e2.add_field(name="メンション可能", value="いいえ")

            channel = discord.utils.get(before.guild.channels, name="幽々子ログ")
            await channel.send(embed=e2)

    @commands.Cog.listener()
    async def on_message_edit(self,before, after):

        embed = discord.Embed(
            title="メッセージが編集されました",
            timestamp=after.created_at,
            description=f"<#{before.channel.id}>で<@!{before.author.id}>がメッセージを編集しました",
            colour=discord.Colour(0x5d00ff)
        )
        embed.set_author(name=f'{before.author.name}#{before.author.discriminator}', icon_url=before.author.avatar_url)
        embed.set_footer(text=f"Author ID:{before.author.id} • Message ID: {before.id}")
        embed.add_field(name='Before:', value=before.content, inline=False)
        embed.add_field(name="After:", value=after.content, inline=False)
        embed.add_field(name="メッセージのURL", value=after.jump_url)
        channel = discord.utils.get(after.guild.channels, name="幽々子ログ")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self,role):
        e = discord.Embed(title="役職の作成", color=0x5d00ff, timestamp=role.created_at)
        e.add_field(name="役職名", value=role.name)

        e.add_field(name="id", value=role.id)

        ch = discord.utils.get(role.guild.channels, name="幽々子ログ")
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_role_delete(self,role):
        e = discord.Embed(title="役職の削除", color=0x5d00ff)
        e.add_field(name="役職名", value=role.name)

        ch = discord.utils.get(role.guild.channels, name="幽々子ログ")
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self,channel):
        e = discord.Embed(title="チャンネル削除", color=0x5d00ff)
        e.add_field(name="チャンネル名", value=channel.name)
        ch = discord.utils.get(channel.guild.channels, name="幽々子ログ")
        await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        channel = discord.utils.get(before.guild.channels, name="幽々子ログ")
        if before.name != after.name:
            embed = discord.Embed(title="channel nameを変更しました",color=0x5d00ff)
            embed.add_field(name="設定前", value=f'`{before.name}`', inline=True)
            embed.add_field(name="設定後", value=f'`{after.name}`', inline=False)
            embed.add_field(name="現在のチャンネル名", value=after.name)
            embed.add_field(name="現在のトピック", value=after.topic)
            embed.add_field(name="nsfwかどうか", value=after.nsfw)
            embed.add_field(name="現在のカテゴリー", value=after.category)
            embed.add_field(name="低速モード", value=after.slowmode_delay)
            embed.add_field(name="タイプ", value=after.type)
            await channel.send(embed=embed)

        if before.topic != after.topic:
            e = discord.Embed(title="チャンネルのトピックが変わりました", color=0x5d00ff)
            e.add_field(name="設定前", value=f'`{before.topic}`')
            e.add_field(name="設定後", value=f'`{after.topic}`')
            e.add_field(name="現在のチャンネル名", value=after.name)
            e.add_field(name="現在のトピック", value=after.topic)
            e.add_field(name="nsfwかどうか", value=after.nsfw)
            e.add_field(name="現在のカテゴリー", value=after.category)
            e.add_field(name="低速モード", value=after.slowmode_delay)
            e.add_field(name="タイプ", value=after.type)
            await channel.send(embed=e)

        if before.nsfw != after.nsfw:
            e1 = discord.Embed(title="nsfwに設定(解除)しました", color=0x5d00ff)
            e1.add_field(name="設定前", value=f'`{before.nsfw}`')
            e1.add_field(name="設定後", value=f'`{after.nsfw}`')
            e1.add_field(name="現在のチャンネル名",value=after.name)
            e1.add_field(name="現在のトピック",value=after.topic)
            e1.add_field(name="nsfwかどうか",value=after.nsfw)
            e1.add_field(name="現在のカテゴリー", value=after.category)
            e1.add_field(name="低速モード", value=after.slowmode_delay)
            e1.add_field(name="タイプ", value=after.type)
            await channel.send(embed=e1)

        if before.category != after.category:
            e2 = discord.Embed(title="別のカテゴリーに移動しました", color=0x5d00ff)
            e2.add_field(name="設定前", value=f'`{before.category}`')
            e2.add_field(name="設定後", value=f'`{after.category}`')
            e2.add_field(name="現在のチャンネル名",value=after.name)
            e2.add_field(name="現在のトピック",value=after.topic)
            e2.add_field(name="nsfwかどうか",value=after.nsfw)
            e2.add_field(name="現在のカテゴリー",value=after.category)
            e2.add_field(name="低速モード", value=after.slowmode_delay)
            e2.add_field(name="タイプ", value=after.type)
            await channel.send(embed=e2)


        if before.slowmode_delay != after.slowmode_delay:
            e4 = discord.Embed(title="低速モードを設定しました", color=0x5d00ff)
            e4.add_field(name="設定前", value=f'`{before.slowmode_delay}秒`')
            e4.add_field(name="設定後", value=f'{after.slowmode_delay}秒')
            e4.add_field(name="現在のチャンネル名",value=after.name)
            e4.add_field(name="現在のトピック",value=after.topic)
            e4.add_field(name="nsfwかどうか",value=after.nsfw)
            e4.add_field(name="現在のカテゴリー", value=after.category)
            e4.add_field(name="低速モード",value=after.slowmode_delay)
            e4.add_field(name="タイプ", value=after.type)
            await channel.send(embed=e4)

        if before.type != after.type:
            e5 = discord.Embed(title="チャンネルのタイプを変更しました", color=0x5d00ff)
            e5.add_field(name="設定前", value=before.type)
            e5.add_field(name="設定後", value=after.type)
            e5.add_field(name="現在のチャンネル名",value=after.name)
            e5.add_field(name="現在のトピック",value=after.topic)
            e5.add_field(name="nsfwかどうか",value=after.nsfw)
            e5.add_field(name="現在のカテゴリー", value=after.category)
            e5.add_field(name="低速モード",value=after.slowmode_delay)
            e5.add_field(name="タイプ",value=after.type)
            await channel.send(embed=e5)




    @commands.Cog.listener()
    async def on_voice_state_update(before, after):
        if before.voice.voice_channel is None and after.voice.voice_channel is not None:
            for channel in before.server.channels:
                if channel.name == 'あざ':
                    await commands.send_message(channel, "Howdy")

    @commands.group(aliases=['ch'], description='チャンネルを操作するコマンド（サブコマンド必須）')
    async def channel(self, ctx):
        """
        チャンネルを管理するコマンド群です。このコマンドだけでは管理できません。半角スペースの後、続けて以下のサブコマンドを入力ください。
        - チャンネルを作成したい場合は、`make`を入力し、チャンネル名を指定してください。
        - プライベートなチャンネルを作成したい場合は`privateMake`を入力し、チャンネル名を指定してください。
        - チャンネルを閲覧できるロールを削除したい場合、`roleDelete`を入力し、ロール名を指定してください。
        - トピックを変更したい場合は、`topic`を入力し、トピックに設定したい文字列を指定してください。
        """
        # サブコマンドが指定されていない場合、メッセージを送信する。
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title="コマンドリスト",color=0x5d00ff)
            e.add_field(name="`channel make <チャンネル名>")

    @channel.command(aliases=['c', 'm', 'mk', 'craft'], description='チャンネルを作成します')
    async def make(self, ctx, channelName=None):
        """
        引数に渡したチャンネル名でテキストチャンネルを作成します（コマンドを打ったチャンネルの所属するカテゴリに作成されます）。
        30秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = ctx.author
        # チャンネル名がない場合は実施不可
        if channelName is None:
            await ctx.message.delete()
            await ctx.channel.send('チャンネル名を指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        # メッセージの所属するカテゴリを取得
        guild = ctx.channel.guild
        category_id = ctx.message.channel.category_id
        category = guild.get_channel(category_id)

        # カテゴリーが存在するなら、カテゴリーについて確認メッセージに記載する
        category_text = ''
        if category is not None:
            category_text = f'カテゴリー「**{category.name}**」に、\n';

        # 念の為、確認する
        confirm_text = f'{category_text}パブリックなチャンネル **{channelName}** を作成してよろしいですか？ 問題ない場合、30秒以内に👌(ok_hand)のリアクションをつけてください。\nあなたのコマンド：`{ctx.message.clean_content}`'
        await ctx.message.delete()
        confirm_msg = await ctx.channel.send(confirm_text)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.TIMEOUT_TIME, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.reply('→リアクションがなかったのでチャンネル作成をキャンセルしました！')
        else:
            try:
                # カテゴリが存在しない場合と存在する場合で処理を分ける
                if category is None:
                    new_channel = await guild.create_text_channel(name=channelName)
                else:
                    # メッセージの所属するカテゴリにテキストチャンネルを作成する
                    new_channel = await category.create_text_channel(name=channelName)
            except discord.errors.Forbidden:
                await confirm_msg.reply('→権限がないため、チャンネル作成できませんでした！')
            else:
                await confirm_msg.reply(f'<#{new_channel.id}>を作成しました！')





    @channel.command(aliases=['p','pm','pmk', 'pcraft', 'primk'], description='プライベートチャンネルを作成します')
    async def privateMake(self, ctx, channelName=None):
        """
        引数に渡したチャンネル名でプライベートなテキストチャンネルを作成します（コマンドを打ったチャンネルの所属するカテゴリに作成されます）。
        30秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = ctx.author

        # チャンネル名がない場合は実施不可
        if channelName is None:
            await ctx.message.delete()
            await ctx.channel.send('チャンネル名を指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        # トップロールが@everyoneの場合は実施不可
        if ctx.author.top_role.position == 0:
            await ctx.message.delete()
            await ctx.channel.send('everyone権限しか保持していない場合、このコマンドは使用できません。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        # メッセージの所属するカテゴリを取得
        guild = ctx.channel.guild
        category_id = ctx.message.channel.category_id
        category = guild.get_channel(category_id)

        # カテゴリーが存在するなら、カテゴリーについて確認メッセージに記載する
        category_text = ''
        if category is not None:
            category_text = f'カテゴリー「**{category.name}**」に、\n';

        # Guildのロールを取得し、@everyone以外のロールで最も下位なロール以上は書き込めるような辞書型overwritesを作成
        permissions = []
        for guild_role in ctx.guild.roles:
            # authorのeveryoneの1つ上のロールよりも下位のポジションの場合
            if guild_role.position < ctx.author.roles[1].position:
                permissions.append(discord.PermissionOverwrite(read_messages=False))
            else:
                permissions.append(discord.PermissionOverwrite(read_messages=True))
        overwrites = dict(zip(ctx.guild.roles, permissions))

        logger.debug('-----author\'s role-----------------------------------------------------------')
        for author_role in ctx.author.roles:
            logger.debug(f'id:{author_role.id}, name:{author_role.name}, position:{author_role.position}')
        logger.debug('-----------------------------------------------------------------')
        logger.debug('-----Guild\'s role-----------------------------------------------------------')
        for guild_role in ctx.guild.roles:
            logger.debug(f'id:{guild_role.id}, name:{guild_role.name}, position:{guild_role.position}')
        logger.debug('-----------------------------------------------------------------')

        # 念の為、確認する
        confirm_text = f'{category_text}プライベートなチャンネル **{channelName}** を作成してよろしいですか()？ 問題ない場合、30秒以内に👌(ok_hand)のリアクションをつけてください。\nあなたのコマンド：`{ctx.message.clean_content}`'
        await ctx.message.delete()
        confirm_message = await ctx.channel.send(confirm_text)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.TIMEOUT_TIME, check=check)
        except asyncio.TimeoutError:
            await confirm_message.delete()
            await ctx.channel.send('＊リアクションがなかったのでキャンセルしました！(プライベートなチャンネルを立てようとしていました。)')
        else:
            try:
                # カテゴリが存在しない場合と存在する場合で処理を分ける
                if category is None:
                    new_channel = await guild.create_text_channel(name=channelName, overwrites=overwrites)
                else:
                    # メッセージの所属するカテゴリにテキストチャンネルを作成する
                    new_channel = await category.create_text_channel(name=channelName, overwrites=overwrites)
            except discord.errors.Forbidden:
                await confirm_message.delete()
                await ctx.channel.send('＊権限がないため、実行できませんでした！(プライベートなチャンネルを立てようとしていました。)')
            else:
                await confirm_message.delete()
                await ctx.channel.send(f'`/channel privateMake`コマンドでプライベートなチャンネルを作成しました！')



    @channel.command(aliases=['t', 'tp'], description='チャンネルにトピックを設定します')
    async def topic(self, ctx, *, topicWord=None):
        """
        引数に渡した文字列でテキストチャンネルのトピックを設定します。
        30秒以内に👌(ok_hand)のリアクションをつけないと実行されませんので、素早く対応ください。
        """
        self.command_author = ctx.author
        # トピックがない場合は実施不可
        if topicWord is None:
            await ctx.message.delete()
            await ctx.channel.send('トピックを指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return

        # 念の為、確認する
        original_topic = ''
        if ctx.channel.topic is not None:
            original_topic = f'このチャンネルには、トピックとして既に**「{ctx.channel.topic}」**が設定されています。\nそれでも、'
        confirm_text = f'{original_topic}このチャンネルのトピックに**「{topicWord}」** を設定しますか？ 問題ない場合、30秒以内に👌(ok_hand)のリアクションをつけてください。\nあなたのコマンド：`{ctx.message.clean_content}`'
        await ctx.message.delete()
        confirm_msg = await ctx.channel.send(confirm_text)

        def check(reaction, user):
            return user == self.command_author and str(reaction.emoji) == '👌'

        # リアクション待ち
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=self.TIMEOUT_TIME, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.reply('→リアクションがなかったので、トピックの設定をキャンセルしました！')
        else:
            # チャンネルにトピックを設定する
            try:
                await ctx.channel.edit(topic=topicWord)
            except discord.errors.Forbidden:
                await confirm_msg.reply('→権限がないため、トピックを設定できませんでした！')
            else:
                await confirm_msg.reply(f'チャンネル「{ctx.channel.name}」のトピックに**「{topicWord}」**を設定しました！')

    @commands.command(aliases=["rcr"], description="役職を作成するよ！\n役職を管理できる人のみ！")
    async def rolecreate(self,ctx, rolename):
        if (
                ctx.guild.me.top_role < ctx.author.top_role and ctx.author.guild_permissions.manage_roles) or ctx.guild.owner == ctx.author:
            role = await ctx.guild.create_role(name=rolename)
            e = discord.Embed(title="操作成功", description=f'{role.mention}を作成したよ～', color=ctx.author.color)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(title="実行エラー", description="私は役職を作成する権限を持ってないよ～", color=0xff0000)
            await ctx.send(embed=e)

    @commands.command(aliases=["rdel"], description="役職を削除するよ！\n役職を管理できる人のみ！")
    async def roledelete(self,ctx, role: discord.Role):
        if (
                ctx.guild.me.top_role < ctx.author.top_role and ctx.author.guild_permissions.manage_roles) or ctx.guild.owner == ctx.author:
            await role.delete()
            e = discord.Embed(title="操作成功", description=f'{role.name}を削除したよ～', color=ctx.author.color)
            await ctx.send(embed=e)
        else:
            e = discord.Embed(title="実行エラー", description="君はコマンドを実行する権限を持ってないよ～", color=0xff0000)
            await ctx.send(embed=e)

    @commands.Cog.listener()
    async def on_message(self, message):
        def _check(m):
            return (m.author == message.author
                    and len(m.mentions)
                    and (datetime.utcnow() - m.created_at).seconds < 60)

        if not message.author.bot:
            if len(list(filter(lambda m: _check(m), self.bot.cached_messages))) >= 3:
                await message.channel.send("Don't spam mentions!", delete_after=10)
                unmutes = await self.mute_members(message, [message.author], 5, reason="Mention spam")

                if len(unmutes):
                    await sleep(5)
                    await self.unmute_members(message.guild, [message.author])

    @commands.Cog.listener()
    async def on_member_join(self,member):
        # On member joins we find a channel called general and if it exists,
        # send an embed welcoming them to our guild
        shared = sum(g.get_member(member.id) is not None for g in self.bot.guilds)

        channel = discord.utils.get(member.guild.text_channels, name="幽々子ログ")
        if channel:
            embed = discord.Embed(
                description='新規参加',
                color=0x5d00ff,

            )

            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="ユーザー名", value=member.mention)
            embed.add_field(name="ユーザーid", value=member.id)
            embed.add_field(name="Joined", value=member.joined_at)
            embed.add_field(name="Created", value=member.created_at)
            embed.add_field(name="共通鯖数",value=shared)
            embed.add_field(name="User Serial", value=len(list(member.guild.members)))
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        # On member remove we find a channel called general and if it exists,
        # send an embed saying goodbye from our guild-
        channel = discord.utils.get(member.guild.text_channels, name="幽々子ログ")
        if channel:
            embed = discord.Embed(
                description=f'さようなら{member.name}さん',
                color=0x5d00ff,
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="ユーザー名", value=member.name)
            embed.add_field(name="ユーザーid", value=member.id)
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):

        if before.name != after.name:
            e = discord.Embed(title="サーバーの名前が変りました", color=0x5d00ff)
            e.add_field(name="変更前", value=f'`{before.name}`')
            e.add_field(name="変更後", value=f'`{after.name}`')
            e.add_field(name="AFKチャンネル", value=after.afk_channel)
            e.add_field(name="地域", value=after.region)
            channel = discord.utils.get(after.channels, name="幽々子ログ")
            await channel.send(embed=e)

        if before.region != after.region:
            e1 = discord.Embed(title="サーバーの地域が変りました", color=0x5d00ff)
            e1.add_field(name="変更前", value=f'`{before.region}`')
            e1.add_field(name="変更後", value=f'`{after.region}`')
            e1.add_field(name="サーバー名", value=after.name)
            e1.add_field(name="AFKチャンネル", value=after.afk_channel)
            channel = discord.utils.get(after.channels, name="幽々子ログ")
            await channel.send(embed=e1)

        if before.afk_channel != after.afk_channel:
            e2 = discord.Embed(title="AFKチャンネルが変りました", color=0x5d00ff)
            e2.add_field(name="変更前", value=f'`{before.afk_channel}`')
            e2.add_field(name="変更前", value=f'`{after.afk_channel}`')
            e2.add_field(name="サーバー名", value=after.name)
            channel = discord.utils.get(after.channels, name="幽々子ログ")
            await channel.send(embed=e2)

        if before.owner != after.owner:
            e3 = discord.Embed(title="サーバーの所有者が変りました", color=0x5d00ff)
            e3.add_field(name="変更前", value=f'`{before.owner}`')
            e3.add_field(name="変更前", value=f'`{after.owner}`')
            e3.add_field(name="サーバー名", value=after.name)
            channel = discord.utils.get(after.channels, name="幽々子ログ")
            await channel.send(embed=e3)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        e = discord.Embed(title="ユーザーがBANされました", color=0x5d00ff)
        e.add_field(name="対象者", value=str(user))
        e.add_field(name="実行者", value=str(bl[0].user))
        e.set_footer(text=f"{guild.name}/{guild.id}")
        channel = discord.utils.get(guild.channels, name="幽々子ログ")
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        bl = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        e = discord.Embed(title="ユーザーのban解除", color=0x5d00ff)
        e.add_field(name="ユーザー名", value=str(user))
        e.add_field(name="Banしたときの実行者", value=str(bl[0].user))
        channel = discord.utils.get(guild.channels, name="幽々子ログ")
        await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            e = discord.Embed(title='ニックネームが変わりました', color=0x5d00ff)
            e.add_field(name="変更前", value=f'`{before.nick}`')
            e.add_field(name="変更後", value=f'`{after.nick}`')
            channel = discord.utils.get(after.guild.channels, name="幽々子ログ")
            await channel.send(embed=e)

        if before.roles != after.roles:
            e1 = discord.Embed(title="アップデーtp")
            if len(before.roles) > len(after.roles):
                e1.add_field(name="変更内容", value="役職除去")
                e1.add_field(name="役職", value=list(
                    set(before.roles) - set(after.roles))[0])
            else:
                e1.add_field(name="変更内容", value="役職付与")
                e1.add_field(name="役職", value=list(
                    set(after.roles) - set(before.roles))[0])
                channel = discord.utils.get(after.guild.channels, name="幽々子ログ")
                await channel.send(embed=e1)

    @commands.group()
    async def welcome(self,ctx):
        e = discord.Embed(title="welcome-setting",description="`y/welcome channel <#チャンネル名>`\n`y/welcome text <参加メッセージ>`\n`y/welcome addrole <ロール>`")
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(log(bot))