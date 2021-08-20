import discord,asyncio
from discord.ext import commands
import platform
from collections import Counter
from utils.language import get_lan
import psutil
import sqlite3,random
from typing import Union
from utils.server_language import get_lan_server
import time, struct,subprocess
class information(commands.Cog) :
    def __init__ (self, bot) :
        self.bot = bot
        self.bot.color = 0x5d00ff

    @staticmethod
    def _getRoles(roles):
        string = ''
        for role in roles[::-1]:
            if not role.is_default():
                string += f'{role.mention}, '
        if string == '':
            return 'None'
        else:
            return string[:-2]

    @staticmethod
    def _getEmojis(emojis):
        string = ''
        for emoji in emojis:
            string += str(emoji)
        if string == '':
            return 'None'
        else:
            return string[:1000]

    @commands.command()
    async def debug(self, ctx):
        mem = psutil.virtual_memory()
        allmem = str(mem.total / 1000000000)[0:3]
        used = str(mem.used / 1000000000)[0:3]
        ava = str(mem.available / 1000000000)[0:3]
        memparcent = mem.percent

        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        e = discord.Embed(title=get_lan(ctx.author.id,"about_status"),
                          url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=1024",
                          color=self.bot.color)
        e.add_field(name=get_lan(ctx.author.id,"Processor"), value="Intel(R) Core(TM) i7 CPU")
        e.add_field(name=get_lan(ctx.author.id,"discord.py_version"), value=dpyVersion)
        e.add_field(name=get_lan(ctx.author.id,"python_version"), value=pythonVersion)
        e.add_field(name="OS", value=f"```{platform.system()} {platform.release()}({platform.version()})```")
        e.add_field(
            name=get_lan(ctx.author.id,"memory"),
            value=f"```{get_lan(ctx.author.id,'all_memory')}:{allmem}GB\n{get_lan(ctx.author.id,'use_amount')}:{used}GB({memparcent}%)\n{get_lan(ctx.author.id,'empty_use')}{ava}GB({100 - memparcent}%)```")

        await ctx.send(embed=e)



    @commands.command()
    async def about(self,ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        channels = str(len(set(self.bot.get_all_channels())))
        total_members = [x.id for x in self.bot.get_all_members()]
        unique_members = set(total_members)
        if len(total_members) == len(unique_members):
            member_count = "{:,}".format(len(total_members))
        else:
            member_count = "{:,} ({:,} unique)".format(len(total_members), len(unique_members))

        guild_count = "{:,}".format(len(self.bot.guilds))

        cog_amnt = 0
        empty_cog = 0
        for cog in self.bot.cogs:
            visible = []
            for c in self.bot.get_cog(cog).get_commands():
                if c.hidden:
                    continue
                visible.append(c)
            if not len(visible):
                empty_cog += 1
                # Skip empty cogs
                continue
            cog_amnt += 1

        cog_count = "{:,} cog".format(cog_amnt)
        # Easy way to append "s" if needed:
        if not len(self.bot.cogs) == 1:
            cog_count += "s"
        if empty_cog:
            cog_count += " [{:,} without commands]".format(empty_cog)

        visible = []
        for command in self.bot.commands:
            if command.hidden:
                continue
            visible.append(command)

        command_count = "{:,}".format(len(visible))
        e = discord.Embed(title=get_lan(ctx.author.id,"bot_name"),
                                        url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=1024",
                                        color=0x5d00ff
                                        )

        e.add_field(name=get_lan(ctx.author.id,"bot_servers"),value=guild_count)
        e.add_field(name=get_lan(ctx.author.id,"bot_users"),value=member_count)
        e.add_field(name=get_lan(ctx.author.id,"about_bot_command"),value=command_count + " (in {})".format(cog_count))
        e.set_thumbnail(
            url="https://cdn.discordapp.com/avatars/757807145264611378/f6e2d7ff1f8092409983a77952670eae.png?size=1024")
        e.add_field(name=get_lan(ctx.author.id,"about_channel_count"),value=channels)
        e.add_field(name=get_lan(ctx.author.id,"discord.py_version"),value=dpyVersion)
        e.add_field(name=get_lan(ctx.author.id,"python_version"),value=pythonVersion)
        e.add_field(name=get_lan(ctx.author.id,"about_invite"),
                    value="https://discord.com/api/oauth2/authorize?client_id=757807145264611378&permissions=0&scope=bot")

        await ctx.send(embed=e)

    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.command(name="userinfo", aliases=["ui"], description="ユーザーの情報")
    async def userinfo(self, ctx, *, user: Union[discord.Member, discord.User,] = None):

        user = user or ctx.author
        e = discord.Embed(color=0xb300ff)
        roles = [r.mention for r in user.roles]
        e.set_author(name=get_lan(ctx.author.id,"ui_about"))
        badges = {
            "staff": "<:staff:836951948745900063>",
            "partner": "<:partner:836950588536127508>",
            "hypesquad": "<:hypesquadevents:724328584789098639>",
            "hypesquad_balance": "<:balance:855966162483281940>",
            "hypesquad_bravery": "<:bravery:855966487956684821>",
            "hypesquad_brilliance":
                "<:brilince:855966748250341396>",
            "premium_since": "test",
            "bug_hunter": "<:bughunt:724588087052861531>",
            "bug_hunter_level_2": "<:bug2:699986097694048327>",
            "verified_bot_developer": "<:verifed:836952740818976770>",
            "early_supporter": "<:earlysupporter:724588086646014034>",

        }
        flags = [
            flag for flag, value in dict(user.public_flags).items() if
            value is True
        ]
        flagstr = ""
        for badge in badges.keys():
            if badge in flags:
                flagstr += f" {badges[badge]} "
        n = False
        if n:
            flagstr += f" <:nitro:724328585418113134>"
        if len(flagstr) != 0:
            e.add_field(name="Badges", value=flagstr)

        db = sqlite3.connect("main.db")
        cursor = db.cursor()

        cursor.execute(
            f"SELECT userid, eval FROM eval WHERE userid = '{user.id}'")

        result = cursor.fetchone()

        if result is None:
            sql = (
                "INSERT INTO eval(userid, eval) VALUES(?, ?)")
            val = (str(user.id), 10)

            cursor.execute(sql, val)
            db.commit()
            return
        evals = 1

        for value in cursor:

            if eval < value[0]:
                evals += 1

        evalss = int(result[1])

        since_created = (ctx.message.created_at - user.created_at).days
        since_joined = (ctx.message.created_at - user.joined_at).days
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        user_joined = user.joined_at.strftime("%d %b %Y %H:%M")

        created_at = f"{user_created}\n({since_created} days ago)"
        joined_at = f"{user_joined}\n({since_joined} days ago)"

        e.add_field(name="ユーザー名", value=f"{user}({user.id})", inline=True)


        voice = getattr(user, 'voice', None)
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
            e.add_field(name=get_lan(ctx.author.id,"ui_voice"), value=voice, inline=True)
        else:
            e.add_field(name=get_lan(ctx.author.id,"ui_voice"), value=get_lan(ctx.author.id,"ui_not_voice"))

        if user.id in [478126443168006164]:  # owner
            e.add_field(name=get_lan(ctx.author.id,"ui_perm"), value=get_lan(ctx.author.id,"ui_owner"))
        elif user.id in [602680118519005184, 385746925040828418]:
            e.add_field(name=get_lan(ctx.author.id,"ui_perm"), value=get_lan(ctx.author.id,"ui_admin"))  # subowner
        else:
            e.add_field(name=get_lan(ctx.author.id,"ui_perm"), value=get_lan(ctx.author.id,"ui_ippan"))

        if user.bot:
            e.add_field(name=get_lan(ctx.author.id,"ui_bot"), value=get_lan(ctx.author.id,"ui_bot_yes"))
        else:
            e.add_field(name=get_lan(ctx.author.id,"ui_bot"), value=get_lan(ctx.author.id,"ui_bot_no"))
        e.add_field(name="ユーザー評価値", value=evalss)
        if str(user.status) == "online":
            e.add_field(name=get_lan(ctx.author.id,"ui_status"), value='<:online:855965213156311091>  ')
        elif str(user.status) == "offline":
            e.add_field(name=get_lan(ctx.author.id,"ui_status"), value='<:offline:855965198221180968>')
        elif str(user.status) == "idle":
            e.add_field(name=get_lan(ctx.author.id,"ui_status"), value='<:afk:855965231740878878>')
        elif str(user.status) == "dnd":
            e.add_field(name=get_lan(ctx.author.id,"ui_status"), value='<:dnd:855965222640156682> ')

        if user.mobile_status:
            e.add_field(name=get_lan(ctx.author.id,"ui_use_mobile"), value=':mobile_phone:')
        elif user.desktop_status:
            e.add_field(name=get_lan(ctx.author.id,"ui_use_desktop"), value=':desktop:')

        elif user.web_status:
            e.add_field(name=get_lan(ctx.author.id,"ui_use_web"), value=':computer:')

        if user.activity is not None:
            try:
                if user.activity.type == discord.ActivityType.custom:
                    e.add_field(name=get_lan(ctx.author.id,"ui_playing"), value=user.activity)
                else:
                    e.add_field(name=get_lan(ctx.author.id,"ui_playing"), value=f'{user.activity.name}')
            except:
                e.add_field(name=get_lan(ctx.author.id,"ui_playing"), value=user.activity)

        e.add_field(name=get_lan(ctx.author.id,"ui_display"), value=user.display_name)

        if bool(user.premium_since):
            e.add_field(name=get_lan(ctx.author.id,"ui_boost"), value=get_lan(ctx.author.id,"ui_boost_yes"))
        else:
            e.add_field(name=get_lan(ctx.author.id,"ui_boost"), value=get_lan(ctx.author.id,"ui_boost_no"))

        e.add_field(name=get_lan(ctx.author.id,"ui_join_discord"), value=created_at, inline=True)
        e.add_field(name=get_lan(ctx.author.id,"ui_join_server"), value=joined_at, inline=True)

        e.add_field(name=get_lan(ctx.author.id,"ui_high_role"), value=user.top_role.mention)

        if roles:
            e.add_field(name=f"Roles({len(roles)})",
                        value=', '.join(roles) if len(roles) < 40 else f'{len(roles)} roles', inline=False)

        e.add_field(name=get_lan(ctx.author.id,"ui_avatar"), value=user.avatar_url, inline=False)

        if user.avatar:
            e.set_thumbnail(url=user.avatar_url)

        if isinstance(user, discord.User):
            e.set_footer(text=get_lan(ctx.author.id,"ui_isnot"))

        role_permission = user.guild_permissions

        server_permission = {
            'administrator': get_lan(ctx.author.id,"ui_administrator"), 'read_messages': get_lan(ctx.author.id,"ui_read_messages"), 'manage_channels': get_lan(ctx.author.id,"ui_manage_channels"),
            'manage_roles': get_lan(ctx.author.id,"ui_manage_roles"), 'manage_emojis': get_lan(ctx.author.id,"ui_manage_emojis"),
            'view_audit_log': get_lan(ctx.author.id,"ui_view_audit_log"), 'view_guild_insights': get_lan(ctx.author.id,"ui_view_guild_insights"),
            'manage_webhooks': get_lan(ctx.author.id,"ui_manage_webhook"), 'manage_guild': get_lan(ctx.author.id,"ui_manage_guild")
        }
        member_permission = {
            'create_instant_invite': get_lan(ctx.author.id,"ui_create_instant_invite"), 'change_nickname': get_lan(ctx.author.id,"ui_change_nickname"),
            'manage_nicknames': get_lan(ctx.author.id,"ui_manage_nicknames"), 'kick_members': get_lan(ctx.author.id,"ui_kick_members"),
            'ban_members': get_lan(ctx.author.id,"ui_ban_members")
        }
        ch_permission = {
            'send_messages': get_lan(ctx.author.id,"ui_send_messages"), 'embed_links': get_lan(ctx.author.id,"ui_embed_links"), 'attach_files': get_lan(ctx.author.id,"ui_attach_files"),
            'add_reactions': get_lan(ctx.author.id,"ui_add_reactions"), 'external_emojis': get_lan(ctx.author.id,"ui_external_emojis"),
            'mention_everyone': get_lan(ctx.author.id,"ui_mention_everyone"), 'manage_messages': get_lan(ctx.author.id,"ui_manage_messages"),
            'read_message_history': get_lan(ctx.author.id,"ui_read_message_history"), 'send_tts_messages': get_lan(ctx.author.id,"ui_send_tts_message"),
            'use_slash_commands': get_lan(ctx.author.id,"ui_use_slash_commands")
        }
        voice_permission = {
            'connect': get_lan(ctx.author.id,"ui_connect"), 'speak': get_lan(ctx.author.id,"ui_speak"), 'stream': get_lan(ctx.author.id,"ui_stream"),
            'use_voice_activation': get_lan(ctx.author.id,"ui_use_voice_activation"), 'priority_speaker': get_lan(ctx.author.id,"ui_priority_speaker"),
            'mute_members': get_lan(ctx.author.id,"ui_mute_members"), 'deafen_members': get_lan(ctx.author.id,"ui_deafen_members"),
            'move_members': get_lan(ctx.author.id,"ui_move_members"), 'request_to_speak': get_lan(ctx.author.id,"ui_request_to_speak")
        }

        s_perm_text = ''
        m_perm_text = ''
        c_perm_text = ''
        not_vperm_text = ''
        not_cperm_text = ''
        not_mperm_text = ''
        not_sperm_text = ''
        v_perm_text = ''
        user_permission_list = []
        for rp in list(role_permission):
            if rp[1]:
                user_permission_list.append(rp[0])

        for sp in list(server_permission):
            if sp in user_permission_list:
                s_perm_text += f"✅:{server_permission[sp]}"
            else:
                not_sperm_text += f"❌:{server_permission[sp]}"
        for sp in list(member_permission):
            if sp in user_permission_list:
                m_perm_text += f"✅:{member_permission[sp]}"
            else:
                not_mperm_text += f"❌:{member_permission[sp]}"
        for sp in list(ch_permission):
            if sp in user_permission_list:
                c_perm_text += f"✅:{ch_permission[sp]}"
            else:
                not_cperm_text += f"❌:{ch_permission[sp]}"
        for sp in list(voice_permission):
            if sp in user_permission_list:
                v_perm_text += f"✅:{voice_permission[sp]}"
            else:
                not_vperm_text += f"❌:{voice_permission[sp]}"

        e.add_field(name=get_lan(ctx.author.id,"ui_all_server"), value=f'`{s_perm_text}`,`{not_sperm_text}`')
        e.add_field(name=get_lan(ctx.author.id,"ui_perm_member"), value=f'`{m_perm_text}`,`{not_mperm_text}`')
        e.add_field(name=get_lan(ctx.author.id,"ui_perm_text"), value=f'`{c_perm_text}`,`{not_cperm_text}`')
        e.add_field(name=get_lan(ctx.author.id,"ui_perm_voice"), value=f'`{v_perm_text}`,`{not_vperm_text}`')

        shared = sum(g.get_member(user.id) is not None for g in self.bot.guilds)
        e.add_field(name="共通鯖数", value=shared)

        await ctx.send(embed=e)

    @commands.command()
    async def serverinfo(self,ctx,guild:discord.Guild=None):
        if guild is not None and await self.bot.is_owner(ctx.author):
            guild = self.bot.get_guild(guild)
            if guild is None:
                return await ctx.send(f'Invalid Guild ID given.')
        else:
            guild = ctx.guild

        if not guild.chunked:
            async with ctx.typing():
                await guild.chunk(cache=True)

        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1


        e = discord.Embed(title=get_lan(ctx.author.id,"si_about"),color=self.bot.color)
        e.add_field(name=get_lan(ctx.author.id,"si_name"),value=f'{guild.name}({guild.id})')
        e.add_field(name=get_lan(ctx.author.id,"si_owner"),value=f'{guild.owner}({guild.owner.id})')

        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        bm = 0
        ubm = 0
        for m in guild.members:
            if m.bot:
                bm = bm + 1
            else:
                ubm = ubm + 1

        e.add_field(name=get_lan(ctx.author.id,"si_member"),value=f"{len(guild.members)}(<:bot:798877222638845952>:{bm}<:user:852849921262616607>{ubm})")
        e.add_field(name=get_lan(ctx.author.id,"si_channel"),value=f'{("<:categorie:798883839124308008>")}:{len(guild.categories)}\n{(":speech_balloon:")}:{len(guild.text_channels)}\n{(":mega:")}:{len(guild.voice_channels)}\n{(":pager:")}:{len(guild.stage_channels)}')

        e.add_field(name=get_lan(ctx.author.id,"si_emoji"),value=len(guild.emojis))
        e.add_field(name=get_lan(ctx.author.id,"si_region"),value=str(guild.region))

        if guild.verification_level == discord.VerificationLevel.none:
            e.add_field(name=get_lan(ctx.author.id,"si_verfiy"),value=get_lan(ctx.author.id,"si_verfiy_none"))
        elif guild.verification_level == discord.VerificationLevel.low:
            e.add_field(name=get_lan(ctx.author.id,"si_verfiy"),value=get_lan(ctx.author.id,"si_verfiy_1"))
        elif guild.verification_level == discord.VerificationLevel.medium:
            e.add_field(name=get_lan(ctx.author.id,"si_verfiy"),value=get_lan(ctx.author.id,"si_verfiy_2"))
        elif ctx.guild.verification_level == discord.VerificationLevel.high:
            e.add_field(name=get_lan(ctx.author.id, "si_verfiy"), value=get_lan(ctx.author.id, "si_verfiy_3"))
        elif ctx.guild.verification_level == discord.VerificationLevel.extreme:
            e.add_field(name=get_lan(ctx.author.id, "si_verfiy"), value=get_lan(ctx.author.id, "si_verfiy_4"))

        if ctx.guild.explicit_content_filter == discord.ContentFilter.disabled:
            e.add_field(name=get_lan(ctx.author.id,"si_filter"),value=get_lan(ctx.author.id,"si_filter_none"))
        elif ctx.guild.explicit_content_filter == discord.ContentFilter.no_role:
            e.add_field(name=get_lan(ctx.author.id, "si_filter"), value=get_lan(ctx.author.id, "si_filter_role"))
        elif ctx.guild.explicit_content_filter == discord.ContentFilter.all_members:
            e.add_field(name=get_lan(ctx.author.id, "si_filter"), value=get_lan(ctx.author.id, "si_filter_member"))


        if guild.afk_channel:
            e.add_field(name=get_lan(ctx.author.id,"si_afk"), value=f"{guild.afk_channel.name}({str(guild.afk_channel.id)})")
            e.add_field(name=get_lan(ctx.author.id,"si_afk_timeout"), value=str(guild.afk_timeout / 60))
        else:
            e.add_field(name=get_lan(ctx.author.id,"si_afk"), value=get_lan(ctx.author.id,"si_afk_none"))

        if guild.system_channel:
            e.add_field(name=get_lan(ctx.author.id,"si_system_channel"), value=f"{guild.system_channel}\n({str(guild.system_channel.id)})")
        try:

            e.add_field(name=get_lan(ctx.author.id,"si_welcome_channel"), value=guild.system_channel_flags.join_notifications)
            e.add_field(name=get_lan(ctx.author.id,"si_boost_channel"), value=guild.system_channel_flags.premium_subscriptions)
        except:
            pass

        emojis = self._getEmojis(guild.emojis)
        e.add_field(name=get_lan_server(ctx.guild.id, "serverlang"), value=get_lan_server(ctx.guild.id,"server_lang"))

        e.add_field(name=get_lan(ctx.author.id,"si_custom_emoji"), value=emojis, inline=False)

        rlist = "@".join([i.name for i in guild.roles])
        if len(rlist) <= 1000:
            e.add_field(name=get_lan(ctx.author.id,"si_roles"), value=rlist)
        e.add_field(name=get_lan(ctx.author.id,"si_features"),
                    value=f"```{','.join(guild.features)}```")
        await ctx.send(embed=e)

    @commands.command()
    async def emojiinfo(self,ctx, *, emj: discord.Emoji = None):
        if emj is None:
            await ctx.send(get_lan(ctx.author.id,"ei_none"))

        else:
            e = discord.Embed(title=get_lan(ctx.author.id,"ei_about"),description=f"id:{emj.id}")
            if emj.animated:
                e.add_field(name=get_lan(ctx.author.id,"ei_animated"),value=get_lan(ctx.author.id,"ei_yes"))
            else:
                e.add_field(name=get_lan(ctx.author.id,"ei_animated"),value=get_lan(ctx.author.id,"ei_no"))

            if emj.available:
                e.add_field(name=get_lan(ctx.author.id, "ei_can_use"), value=get_lan(ctx.author.id, "ei_yes_use"))
            else:
                e.add_field(name=get_lan(ctx.author.id, "ei_can_use"), value=get_lan(ctx.author.id, "ei_no_use"))

            if emj.managed:
                e.add_field(name=get_lan(ctx.author.id, "ei_managed"), value=get_lan(ctx.author.id, "ei_yes"))
            else:
                e.add_field(name=get_lan(ctx.author.id, "ei_managed"), value=get_lan(ctx.author.id, "ei_no"))

            e.add_field(name="url", value=emj.url)
            e.set_thumbnail(url=emj.url)
            e.timestamp = emj.created_at
            await ctx.send(embed=e)


    @commands.command(name="roleinfo",aliases=["ri"])
    async def roleinfo(self, ctx, *, role: commands.RoleConverter = None):
        if role is None:
            await ctx.send(get_lan(ctx.author.id,"ri_none"))
        elif role.guild == ctx.guild:
            e = discord.Embed(title=get_lan(ctx.author.id, "ri_about"), description=f"id:{role.id}",
                              color=self.bot.color)
            if role.hoist:
                e.add_field(name=get_lan(ctx.author.id,"ri_hoist"),value=get_lan(ctx.author.id,"ri_yes"))
            else:
                e.add_field(name=get_lan(ctx.author.id, "ri_hoist"), value=get_lan(ctx.author.id, "ri_no"))

            if role.mentionable:
                e.add_field(name=get_lan(ctx.author.id,"ri_mention"),value=get_lan(ctx.author.id,"ri_yes"))
            else:
                e.add_field(name=get_lan(ctx.author.id, "ri_mention"), value=get_lan(ctx.author.id, "ri_no"))

            e.add_field(name=get_lan(ctx.author.id,"ri_members"), value=str(len(role.members)))
            e.add_field(name=get_lan(ctx.author.id,"ri_color"), value=str(role.color))

            e.add_field(name=get_lan(ctx.author.id,"ri_create"), value=role.created_at.__format__('%x at %X'))
            e.add_field(name='メンバー [%s]' % len(role.members),
                            value='%s Online' % sum(1 for m in role.members if m.status != discord.Status.offline),
                            inline=True)

            hasmember = ""
            for m in role.members:
                hasmember = hasmember + f"{m.mention},"
            if not hasmember == "":
                if len(hasmember) <= 1024:
                    e.add_field(name=get_lan(ctx.author.id,"ri_member"), value=hasmember)
                else:
                    e.add_field(name=get_lan(ctx.author.id,"ri_member"), value=get_lan(ctx.author.id,"ri_too"))
            else:
                e.add_field(name=get_lan(ctx.author.id,"ri_member"), value=get_lan(ctx.author.id,"ri_none_membe"))

            role_permission = role.permissions

            server_permission = {
                'administrator': get_lan(ctx.author.id, "ui_administrator"),
                'read_messages': get_lan(ctx.author.id, "ui_read_messages"),
                'manage_channels': get_lan(ctx.author.id, "ui_manage_channels"),
                'manage_roles': get_lan(ctx.author.id, "ui_manage_roles"),
                'manage_emojis': get_lan(ctx.author.id, "ui_manage_emojis"),
                'view_audit_log': get_lan(ctx.author.id, "ui_view_audit_log"),
                'view_guild_insights': get_lan(ctx.author.id, "ui_view_guild_insights"),
                'manage_webhooks': get_lan(ctx.author.id, "ui_manage_webhook"),
                'manage_guild': get_lan(ctx.author.id, "ui_manage_guild")
            }
            member_permission = {
                'create_instant_invite': get_lan(ctx.author.id, "ui_create_instant_invite"),
                'change_nickname': get_lan(ctx.author.id, "ui_change_nickname"),
                'manage_nicknames': get_lan(ctx.author.id, "ui_manage_nicknames"),
                'kick_members': get_lan(ctx.author.id, "ui_kick_members"),
                'ban_members': get_lan(ctx.author.id, "ui_ban_members")
            }
            ch_permission = {
                'send_messages': get_lan(ctx.author.id, "ui_send_messages"),
                'embed_links': get_lan(ctx.author.id, "ui_embed_links"),
                'attach_files': get_lan(ctx.author.id, "ui_attach_files"),
                'add_reactions': get_lan(ctx.author.id, "ui_add_reactions"),
                'external_emojis': get_lan(ctx.author.id, "ui_external_emojis"),
                'mention_everyone': get_lan(ctx.author.id, "ui_mention_everyone"),
                'manage_messages': get_lan(ctx.author.id, "ui_manage_messages"),
                'read_message_history': get_lan(ctx.author.id, "ui_read_message_history"),
                'send_tts_messages': get_lan(ctx.author.id, "ui_send_tts_message"),
                'use_slash_commands': get_lan(ctx.author.id, "ui_use_slash_commands")
            }
            voice_permission = {
                'connect': get_lan(ctx.author.id, "ui_connect"), 'speak': get_lan(ctx.author.id, "ui_speak"),
                'stream': get_lan(ctx.author.id, "ui_stream"),
                'use_voice_activation': get_lan(ctx.author.id, "ui_use_voice_activation"),
                'priority_speaker': get_lan(ctx.author.id, "ui_priority_speaker"),
                'mute_members': get_lan(ctx.author.id, "ui_mute_members"),
                'deafen_members': get_lan(ctx.author.id, "ui_deafen_members"),
                'move_members': get_lan(ctx.author.id, "ui_move_members"),
                'request_to_speak': get_lan(ctx.author.id, "ui_request_to_speak")
            }

            s_perm_text = ''
            m_perm_text = ''
            c_perm_text = ''
            not_vperm_text = ''
            not_cperm_text = ''
            not_mperm_text = ''
            not_sperm_text = ''
            v_perm_text = ''
            user_permission_list = []
            for rp in list(role_permission):
                if rp[1]:
                    user_permission_list.append(rp[0])

            for sp in list(server_permission):
                if sp in user_permission_list:
                    s_perm_text += f"✅:{server_permission[sp]}"
                else:
                    not_sperm_text += f"❌:{server_permission[sp]}"
            for sp in list(member_permission):
                if sp in user_permission_list:
                    m_perm_text += f"✅:{member_permission[sp]}"
                else:
                    not_mperm_text += f"❌:{member_permission[sp]}"
            for sp in list(ch_permission):
                if sp in user_permission_list:
                    c_perm_text += f"✅:{ch_permission[sp]}"
                else:
                    not_cperm_text += f"❌:{ch_permission[sp]}"
            for sp in list(voice_permission):
                if sp in user_permission_list:
                    v_perm_text += f"✅:{voice_permission[sp]}"
                else:
                    not_vperm_text += f"❌:{voice_permission[sp]}"

            e.add_field(name=get_lan(ctx.author.id, "ui_all_server"), value=f'`{s_perm_text}`,`{not_sperm_text}`')
            e.add_field(name=get_lan(ctx.author.id, "ui_perm_member"), value=f'`{m_perm_text}`,`{not_mperm_text}`')
            e.add_field(name=get_lan(ctx.author.id, "ui_perm_text"), value=f'`{c_perm_text}`,`{not_cperm_text}`')
            e.add_field(name=get_lan(ctx.author.id, "ui_perm_voice"), value=f'`{v_perm_text}`,`{not_vperm_text}`')
            await ctx.send(embed=e)

    @commands.command(name="avatar", description="ユーザーのアイコン")
    async def avatar(self, ctx, *, user: Union[discord.Member, discord.User] = None):
        """`誰でも`"""
        embed = discord.Embed(color=0x5d00ff)
        user = user or ctx.author
        avatar = user.avatar_url_as(static_format='png')
        embed.set_author(name=str(user), url=avatar)
        embed.set_image(url=avatar)
        await ctx.send(embed=embed)

    @commands.command()
    async def channelinfo(self,ctx,target=None):
        if target is None:
            target = ctx.channel
        else:
            try:
                target = await commands.TextChannelConverter().convert(ctx, target)
            except:
                try:
                    target = await commands.VoiceChannelConverter().convert(ctx, target)
                except:
                    try:
                        target = await commands.CategoryChannelConverter().convert(ctx, target)
                    except:
                        try:
                            target = self.bot.get_channel(int(target))
                        except:
                            await ctx.send(get_lan(ctx.author.id,"ch_not_see"))
                            return
        if not target.guild.id == ctx.guild.id:
            await ctx.send(get_lan(ctx.author.id,"ch_betu"))
            return
        if isinstance(target, discord.TextChannel):
            if target.is_news():
                if "NEWS" in target.guild.features:
                    e = discord.Embed(title=get_lan(ctx.author.id,"ch_about"),description=get_lan(ctx.author.id,"ch_type_ann"),color=self.bot.color)
                else:
                    e = discord.Embed(title=get_lan(ctx.author.id,"ch_about"),description=get_lan(ctx.author.id,"ch_type_ann_no"),color=self.bot.color)
            else:
                e = discord.Embed(title=get_lan(ctx.author.id,"ch_about"),description=get_lan(ctx.author.id,"ch_type_text"),color=self.bot.color)
            e.add_field(name=get_lan(ctx.author.id,"ch_name"),value=f'{target.name}({target.id})')
            e.timestamp = target.created_at
            if target.category:
                e.add_field(name=get_lan(ctx.author.id,"ch_join_category"), value=f"{target.category.name}({target.category.id})")
            e.add_field(name=get_lan(ctx.author.id,"ch_topic"), value=target.topic or get_lan(ctx.author.id,"ch_topic_no"))
            if not target.slowmode_delay == 0:
                e.add_field(name=get_lan(ctx.author.id,"ch_slowmode"), value=f"{target.slowmode_delay}秒")
            if target.is_nsfw():
                e.add_field(name=get_lan(ctx.author.id,"ch_nsfw"), value=get_lan(not ctx.author.id,"ch_yes"))
            else:
                e.add_field(name=get_lan(ctx.author.id,"ch_nsfw"), value=get_lan(not ctx.author.id,"ch_no"))

            mbs = ""
            for m in target.members:
                if len(mbs + f"`{m.name}`,") >= 1020:
                    mbs = mbs + f"他"
                    break
                else:
                    mbs = mbs + f"`{m.name}`,"
            if mbs != "":
                e.add_field(name=f"{get_lan(ctx.author.id, 'ri_member')}({len(target.members)}人)", value=mbs, inline=False)
            await ctx.send(embed=e)
        elif isinstance(target, discord.VoiceChannel):
            e = discord.Embed(name=get_lan(ctx.author.id,"ch_about"), description=get_lan(ctx.author.id,"ch_type_voice"),color=self.bot.color)
            e.timestamp = target.created_at
            e.add_field(name=get_lan(ctx.author.id, "ch_name"), value=f'{target.name}({target.id})')
            if target.category:
                e.add_field(name=get_lan(ctx.author.id, "ch_join_category"),
                            value=f"{target.category.name}({target.category.id})")
            e.add_field(name=get_lan(ctx.author.id,"ch_bitrate"), value=f"{target.bitrate / 1000}Kbps")
            if not target.user_limit == 0:
                e.add_field(name=get_lan(ctx.author.id,"ch_limite"), value=f"{target.user_limit}人")
            e.add_field(name=get_lan(ctx.author.id,"ch_voice_region"),value=target.rtc_region)

            mbs = ""
            for m in target.members:
                if len(mbs + f"`{m.name}`,") >= 1020:
                    mbs = mbs + f"他"
                    break
                else:
                    mbs = mbs + f"`{m.name}`,"
            if mbs != "":
                e.add_field(name=f"{get_lan(ctx.author.id,'ri_member')}({len(target.members)}人)", value=mbs, inline=False)
            await ctx.send(embed=e)

        elif isinstance(target, discord.CategoryChannel):
            e = discord.Embed(name=get_lan(ctx.author.id,"ch_about"), description=get_lan(ctx.author.id,"ch_type_category"),color=self.bot.color)
            e.timestamp = target.created_at
            e.add_field(name=get_lan(ctx.author.id, "ch_name"), value=f'{target.name}({target.id})')
            if target.is_nsfw():
                e.add_field(name=get_lan(ctx.author.id,"ch_nsfw"), value=get_lan(not ctx.author.id,"ch_yes"))
            else:
                e.add_field(name=get_lan(ctx.author.id,"ch_nsfw"), value=get_lan(not ctx.author.id,"ch_no"))
            mbs = ""
            for c in target.channels:
                if c.type is discord.ChannelType.news:
                    if "NEWS" in target.guild.features:
                        chtype = get_lan(ctx.author.id,"ch_ann")
                    else:
                        chtype = get_lan(ctx.author.id,"ch_ann_no")
                elif c.type is discord.ChannelType.store:
                    chtype = get_lan(ctx.author.id,"ch_news_store")
                elif c.type is discord.ChannelType.voice:
                    chtype = get_lan(ctx.author.id,"ch_news_voice")
                elif c.type is discord.ChannelType.text:
                    chtype = get_lan(ctx.author.id,"ch_news_text")
                else:
                    chtype = str(c.type)
                if len(mbs + f"`{c.name}({chtype})`,") >= 1020:
                    mbs = mbs + f"他"
                    break
                else:
                    mbs = mbs + f"`{c.name}({chtype})`,"
            if mbs != "":
                e.add_field(name=f"{get_lan(ctx.author.id,'ch_join_channel')}({len(target.channels)}チャンネル)", value=mbs, inline=False)
            await ctx.send(embed=e)
        elif isinstance(target, discord.StageChannel):
            e = discord.Embed(name=get_lan(ctx.author.id, "ch_about"),
                              description=get_lan(ctx.author.id, "ch_type_category"), color=self.bot.color)
            e.add_field(name=get_lan(ctx.author.id, "ch_name"), value=f'{target.name}({target.id})')
            e.timestamp = target.created_at
            if target.category:
                e.add_field(name=get_lan(ctx.author.id, "ch_join_category"),
                            value=f"{target.category.name}({target.category.id})")

            if not target.user_limit == 0:
                e.add_field(name=get_lan(ctx.author.id,"ch_limite"), value=f"{target.user_limit}人")
            mbs = ""
            for m in target.members:
                if len(mbs + f"`{m.name}`,") >= 1020:
                    mbs = mbs + f"他"
                    break
                else:
                    mbs = mbs + f"`{m.name}`,"
            if mbs != "":
                e.add_field(name=f"{get_lan(ctx.author.id,'ri_member')}({len(target.members)}人)", value=mbs, inline=False)
            await ctx.send(embed=e)

    @commands.command(name="messageinfo", aliases=["msg", "message"], description="メッセージの情報")
    async def messageinfo(self, ctx, target:discord.Message):
        """`誰でも`"""
        if target:
            fetch_from = "引数"
            msg = target
        else:
            if ctx.message.reference and ctx.message.type == discord.MessageType.default:
                if ctx.message.reference.cached_message:
                    fetch_from = "返信"
                    msg = ctx.message.reference.cached_message
                else:
                    try:
                        fetch_from = "返信"
                        msg = await self.bot.get_channel(ctx.message.reference.channel_id).fetch_message(
                            ctx.message.reference.message_id)
                    except:
                        fetch_from = "コマンド実行メッセージ"
                        msg = ctx.message

            else:
                fetch_from = "コマンド実行メッセージ"
                msg = ctx.message

        e = discord.Embed(title=f"メッセージ{fetch_from}", descriptio=msg.system_content, color=0x5d00ff)
        e.set_author(name=f"{msg.author.display_name}({msg.author.id}){'[bot]' if msg.author.bot else ''}のメッセージ",
                     icon_url=msg.author.avatar_url_as(static_format="png"))

        post_time = msg.created_at.strftime("%d/%m/%Y %H:%M:%S")

        if msg.edited_at:
            edit_time = msg.edited_at.strftime("%d/%m/%Y %H:%M:%S")

        else:
            edit_time = "なし"

        e.set_footer(text=f"メッセージ送信時間:{post_time}/最終編集時間:{edit_time}")

        e.add_field(name="メッサ",value=msg.content)

        e.add_field(name="メッセージ", value=str(msg.id))
        e.add_field(name="システムメッセージ？", value=msg.is_system())
        e.add_field(name="添付ファイル数", value=f"{len(msg.attachments)}個")
        e.add_field(name="埋め込み数", value=f"{len(msg.embeds)}個")

        if msg.guild.rules_channel and msg.channel_id == msg.guild.rules_channel.id:
            chtype = f"{msg.channel.name}({msg.channel.id}):ルールチャンネル"
        elif msg.channel.is_news():
            chtype = f"{msg.Channel.name}({msg.channel.id}):アナウンスチャンネル"
        else:
            chtype = f"{msg.channel.name}({msg.channel.id}):テキストチャンネル"
        e.add_field(name="メッセージの送信チャンネル", value=chtype)

        if msg.reference:
            e.add_field(name="メッセージの返信等", value=f"返信元確認用:`{msg.reference.channel_id}-{msg.reference.message_id}`")

        e.add_field(name="メンションの内訳",
                    value=f"全員宛メンション:{msg.mention_everyone}\nユーザーメンション:{len(msg.mentions)}個\n役職メンション:{len(msg.role_mentions)}個\nチャンネルメンション:{len(msg.channel_mentions)}個")
        if msg.webhook_id:
            e.add_field(name="webhook投稿", value=f"ID:{msg.webhook_id}")
        e.add_field(name="ピン留めされてるかどうか", value=str(msg.pinned))
        if len(msg.reactions) != 0:
            e.add_field(name="リアクション", value=",".join({f"{r.emoji}:{r.count}" for r in msg.reactions}))

        e.add_field(name="メッセージフラグ", value=[i[0] for i in iter(msg.flags) if i[1]])

        e.add_field(name="メッセージに飛ぶ", value=msg.jump_url)

        try:
            await ctx.replay(embed=e, mentions_author=False)
        except:
            await ctx.send(embed=e)

    @commands.command(name="dir", usage="dir member <ゆーざーid>", description="引数を選択した不和オブジェクトに変換します")
    async def get_object(self, ctx, object, arg, *, attr=None):
        """`誰でも`"""

        object = object.replace(" ", "").lower()
        objects = {
            "member": commands.MemberConverter(),
            "user": commands.UserConverter(),
            "message": commands.MessageConverter(),
            "text": commands.TextChannelConverter(),
            "voice": commands.VoiceChannelConverter(),
            "category": commands.CategoryChannelConverter(),
            "invite": commands.InviteConverter(),
            "role": commands.RoleConverter(),
            "game": commands.GameConverter(),
            "colour": commands.ColourConverter(),
            "color": commands.ColorConverter(),
            "emoji": commands.EmojiConverter(),
            "partial": commands.PartialEmojiConverter(),
        }

        if object not in objects:
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    description="```Could not find object```",
                )
            )

        try:
            obj = await objects[object].convert(ctx, arg)
        except commands.BadArgument:
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(), description="```Conversion failed```"
                )
            )

        if attr:
            attributes = attr.split(".")
            try:
                for attribute in attributes:
                    obj = getattr(obj, attribute)
            except AttributeError:
                return await ctx.send(f"{obj} has no attribute {attribute}")
            return await ctx.send(f"```{obj}\n\n{dir(obj)}```")

        await ctx.send(f"```{obj}\n\n{dir(obj)}```")



def setup(bot):
    bot.add_cog(information(bot))
