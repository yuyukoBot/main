import re
import random
import asyncio

import discord
from discord.ext import commands

from utils.util import GetMessage

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


def convert(argument):
    args = argument.lower()
    matches = re.findall(time_regex, args)
    time = 0
    for key, value in matches:
        try:
            time += time_dict[value] * float(key)
        except KeyError:
            raise commands.BadArgument(
                f"{value} is an invalid time key! h|m|s|d are valid arguments"
            )
        except ValueError:
            raise commands.BadArgument(f"{key} is not a number!")
    return round(time)


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="giveaway",
        description="Create a full giveaway!"
    )
    @commands.guild_only()
    async def giveaway(self, ctx):
        await ctx.send("このプレゼントを始めましょう、私が尋ねる質問に答えてください、そして私たちは先に進みます")

        questionList = [
            ["チャンネルを指定してください", "Mention the channel"],
            ["抽選期間はどれぐらいにしますか", "`d|h|m|s`"],
            ["何をGiveawayしますか?", "ここに書いてください"]
        ]
        answers = {}

        for i, question in enumerate(questionList):
            answer = await GetMessage(self.bot, ctx, question[0], question[1])

            if not answer:
                await ctx.send("You failed to answer, please answer quicker next time.")
                return

            answers[i] = answer

        embed = discord.Embed(name="Giveaway content")
        for key, value in answers.items():
            embed.add_field(name=f"Question: `{questionList[key][0]}`", value=f"Answer: `{value}`", inline=False)

        m = await ctx.send("これらはすべて有効ですか？", embed=embed)
        await m.add_reaction('<:outline_done_outline_black_18dp:809103360388366357>')
        await m.add_reaction("🇽")

        try:
            reaction, member = await self.bot.wait_for(
                "reaction_add",
                timeout=60,
                check=lambda reaction, user: user == ctx.author
                                             and reaction.message.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            await ctx.send("Confirmation Failure. Please try again.")
            return

        if str(reaction.emoji) not in ['<:outline_done_outline_black_18dp:809103360388366357>', "🇽"] or str(reaction.emoji) == "🇽":
            await ctx.send("Cancelling giveaway!")
            return

        channelId = re.findall(r"[0-9]+", answers[0])[0]
        channel = self.bot.get_channel(int(channelId))

        time = convert(answers[1])

        giveawayEmbed = discord.Embed(
            title="🎉 __**Giveaway**__ 🎉",
            description=answers[2]
        )
        giveawayEmbed.set_footer(text=f"This giveaway ends {time} seconds from this message.")
        giveawayMessage = await channel.send(embed=giveawayEmbed)
        await giveawayMessage.add_reaction("🎉")

        await asyncio.sleep(time)

        message = await channel.fetch_message(giveawayMessage.id)
        users = await message.reactions[0].users().flatten()
        users.pop(users.index(ctx.guild.me))
        users.pop(users.index(ctx.author))

        if len(users) == 0:
            await channel.send("No winner was decided")
            return

        winner = random.choice(users)

        await channel.send(f"**Congrats {winner.mention}!**\nPlease contact {ctx.author.mention} about your prize.")


def setup(bot):
    bot.add_cog(Giveaway(bot))
