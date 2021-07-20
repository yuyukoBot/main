import random
import discord
from discord.ext import commands


class GuildSetting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def new(self, ctx):
        await ctx.send("Invalid sub-command passed.")

    @new.command(
        name="category",
        description="Create a new category",
        usage="<role> <Category name>",
    )
    @commands.has_permissions(manage_channels=True)
    async def category(self, ctx, role: discord.Role, *, name):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            role: discord.PermissionOverwrite(read_messages=True),
        }
        category = await ctx.guild.create_category(name=name, overwrites=overwrites)
        await ctx.send(f"Hey dude, I made {category.name} for ya!")

    @new.command(
        name="channel",
        description="Create a new channel",
        usage="<role> <channel name>",
    )
    @commands.has_permissions(manage_channels=True)
    async def channel(self, ctx,*,name):
        await ctx.send("logとして設定したいチャンネルidを送信してください")
        message = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel)
        category = [await commands.converter.CategoryChannelConverter().convert(ctx, logtext) for logtext
                       in message.content.split()]
        for category in category:
            category = category
        mes = await ctx.send('トピックを設定してください')
        def check(react, usr):
            return (
                    react.message.channel == mes.channel
                    and usr == ctx.author
                    and react.message.id == mes.id
                    and react.me
            )
        topic = await self.bot.wait_for("message", check=check)

        await ctx.guild.create_text_channel(name, category=category,topic=topic)



        await ctx.send(f"Hey dude, I made for ya!")


    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_channels=True)
    async def delete(self, ctx):
        await ctx.send("Invalid sub-command passed")

    @delete.command(
        name="category", description="Delete a category", usage="<category> [reason]"
    )
    @commands.has_permissions(manage_channels=True)
    async def _category(self, ctx, category: discord.CategoryChannel, *, reason=None):
        await category.delete(reason=reason)
        await ctx.send(f"hey! I deleted {category.name} for you")

    @delete.command(
        name="channel", description="Delete a channel", usage="<channel> [reason]"
    )
    @commands.has_permissions(manage_channels=True)
    async def _channel(self, ctx, channel: discord.TextChannel = None, *, reason=None):
        channel = channel or ctx.channel
        await channel.delete(reason=reason)
        await ctx.send(f"hey! I deleted {channel.name} for you")

    @commands.command(
        name="lockdown",
        description="Lock, or unlock the given channel!",
        usage="[channel]",
    )
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        if ctx.guild.default_role not in channel.overwrites:
            # This is the same as the elif except it handles agaisnt empty overwrites dicts
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False)
            }
            await channel.edit(overwrites=overwrites)
            await ctx.send(f"I have put {channel.name} on lockdown.")
        elif (
                channel.overwrites[ctx.guild.default_role].send_messages == True
                or channel.overwrites[ctx.guild.default_role].send_messages == None
        ):
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
            await ctx.send(f"I have put {channel.name} on lockdown.")
        else:
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
            await ctx.send(f"I have removed {channel.name} from lockdown.")


def setup(bot):
    bot.add_cog(GuildSetting(bot))