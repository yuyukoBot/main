import discord
from discord.ext import commands
import asyncio
import functools
import itertools
import random
import youtube_dl
import async_timeout
import sr_api
import os
api = sr_api.Client()
try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class VoiceError(Exception):
    pass


class YTDLError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
        "restrictfilenames": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "ignoreerrors": False,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "source_address": "0.0.0.0",
    }

    FFMPEG_OPTIONS = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn",
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)
    ytdl.cache.remove()

    def __init__(
            self,
            ctx: commands.Context,
            source: discord.FFmpegPCMAudio,
            *,
            data: dict,
            volume: float = 0.5,
    ):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        date = data.get("upload_date")
        self.upload_date = date[6:8] + "." + date[4:6] + "." + date[0:4]
        self.title = data.get("title")
        self.thumbnail = data.get("thumbnail")
        self.description = data.get("description")
        self.duration = self.parse_duration(int(data.get("duration")))
        self.tags = data.get("tags")
        self.url = data.get("webpage_url")
        self.views = data.get("view_count")
        self.likes = data.get("like_count")
        self.dislikes = data.get("dislike_count")
        self.stream_url = data.get("url")

    def __str__(self):
        return f"**{self.title}** by **{self.uploader}**"

    @classmethod
    async def create_source(
            cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None
    ):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(
            cls.ytdl.extract_info, search, download=False, process=False
        )
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError("Couldn't find anything that matches `{search}`")

        if "entries" not in data:
            process_info = data
        else:
            process_info = None
            for entry in data["entries"]:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError(f"Couldn't find anything that matches `{search}`")

        webpage_url = process_info["webpage_url"]
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError(f"Couldn't fetch `{webpage_url}`")

        if "entries" not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info["entries"].pop(0)
                except IndexError:
                    raise YTDLError(
                        f"Couldn't retrieve any matches for `{webpage_url}`"
                    )

        return cls(
            ctx, discord.FFmpegPCMAudio(info["url"], **cls.FFMPEG_OPTIONS), data=info
        )

    @classmethod
    async def search_source(
            cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None
    ):
        channel = ctx.channel
        loop = loop or asyncio.get_event_loop()

        cls.search_query = f"ytsearch10:{''.join(search)}"

        partial = functools.partial(
            cls.ytdl.extract_info, cls.search_query, download=False, process=False
        )
        info = await loop.run_in_executor(None, partial)

        cls.search = {}
        cls.search["title"] = f"Search results for:\n**{search}**"
        cls.search["type"] = "rich"
        cls.search["color"] = 7506394
        cls.search["author"] = {
            "name": f"{ctx.author.name}",
            "url": f"{ctx.author.avatar_url}",
            "icon_url": f"{ctx.author.avatar_url}",
        }

        lst = []
        VIds = []

        for index, e in enumerate(info["entries"]):
            # lst.append(f'`{info["entries"].index(e) + 1}.` {e.get("title")} **[{YTDLSource.parse_duration(int(e.get("duration")))}]**\n')
            VId = e.get("id")
            VUrl = f"https://www.youtube.com/watch?v={VId}"
            VIds.append(VId)
            lst.append(f'`{index + 1}.` [{e.get("title")}]({VUrl})\n')

        lst.append("\n**Type a number to make a choice, Type `cancel` to exit**")
        cls.search["description"] = "\n".join(lst)

        em = discord.Embed.from_dict(cls.search)
        await ctx.send(embed=em, delete_after=45.0)

        def check(msg):
            return (
                    msg.content.isdigit() is True
                    and msg.channel == channel
                    or msg.content.lower() == "cancel"
            )

        try:
            m = await ctx.bot.wait_for("message", check=check, timeout=45.0)

        except asyncio.TimeoutError:
            rtrn = "timeout"

        else:
            if m.content.isdigit() is True:
                sel = int(m.content)
                if 0 < sel <= 10:
                    if info.get("entries"):
                        VId = VIds[sel - 1]
                        VUrl = f"https://www.youtube.com/watch?v={VId}"
                        partial = functools.partial(
                            cls.ytdl.extract_info, VUrl, download=False
                        )
                        data = await loop.run_in_executor(None, partial)
                    rtrn = cls(
                        ctx,
                        discord.FFmpegPCMAudio(data["url"], **cls.FFMPEG_OPTIONS),
                        data=data,
                    )
                else:
                    rtrn = "sel_invalid"
            elif m.content.lower() == "cancel":
                rtrn = "cancel"
            else:
                rtrn = "sel_invalid"

        return rtrn

    @staticmethod
    def parse_duration(duration: int):
        if duration > 0:
            minutes, seconds = (duration // 60, duration % 60)
            hours, minutes = (minutes // 60, minutes % 60)
            days, hours = (hours // 24, hours % 24)

            duration = []
            if days > 0:
                duration.append(f"{days}")
            if hours > 0:
                duration.append(f"{hours}")
            if minutes > 0:
                duration.append(f"{minutes}")
            if seconds >= 0:
                duration.append(f"{seconds:0>2}")

            value = ":".join(duration)

        elif duration == 0:
            value = "LIVE"

        return value


class Song:
    __slots__ = ("source", "requester")

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester


    def create_embed(self):
        if self.source.duration == "":
            DURATION = "/"
        else:
            DURATION = self.source.duration
        embed = (
            discord.Embed(
                title="再生中の曲",
                description=f"```css\n{self.source.title}\n```",
                color=discord.Color.blurple(),
            )
                .add_field(name="再生時間", value=DURATION)
                .add_field(name="リクエストした人", value=self.requester.mention)
                .add_field(
                name="アップロードした人",
                value=f"[{self.source.uploader}]({self.source.uploader_url})",
            )
                .add_field(name="URL", value=f"[Click]({self.source.url})")
                .add_field(name="再生数",value=self.source.views)
                .set_thumbnail(url=self.source.thumbnail)
                .set_author(name=self.requester.name, icon_url=self.requester.avatar_url)
        )
        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.exists = True

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()
            self.now = None

            if self.loop is False:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with async_timeout.timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    self.exists = False
                    return

                self.current.source.volume = self._volume
                self.voice.play(self.current.source, after=self.play_next_song)
                await self.current.source.channel.send(
                    embed=self.current.create_embed()
                )

            # If the song is looped
            elif self.loop is True:
                self.now = discord.FFmpegPCMAudio(
                    self.current.source.stream_url, **YTDLSource.FFMPEG_OPTIONS
                )
                self.voice.play(self.now, after=self.play_next_song)

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class music(commands.Cog):
    """Commands related to music."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state or not state.exists:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage(self.__cog_name__)

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    @commands.command(name="join",description="現在の音声チャネルに参加します")
    async def _join(self, ctx: commands.Context):
        """`誰でも`"""
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name="summon",description="指定したチャンネルにbotを入出させます")
    async def _summon(
            self, ctx: commands.Context, *, channel: discord.VoiceChannel = None
    ):
        """`誰でも`
        """
        if not channel and not ctx.author.voice:
            raise VoiceError(
                "チャンネルに接続していません"
            )

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name="leave", aliases=["disconnect"],description="botをボイスチャンネルから退出させます")
    async def _leave(self, ctx: commands.Context):
        """`誰でも`"""
        if not ctx.voice_state.voice:
            return await ctx.send("ボイスチャンネルに接続していません")

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name="volume",description="音量を調節します")
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """`誰でも`
        """
        if not ctx.voice_state.is_playing:
            return await ctx.send("現在、何も再生されていません。")

        if 0 > volume > 100:
            return await ctx.send("ボリュームは0〜100の間である必要があります")

        ctx.voice_state.current.source.volume = volume / 100
        await ctx.send(f"{volume}%にセットしました")

    @commands.command(name="now", aliases=["np", "playing", "n"],description="現在流してる曲を表示します")
    async def _now(self, ctx: commands.Context):
        """誰でも"""
        embed = ctx.voice_state.current.create_embed()
        await ctx.send(embed=embed)

    @commands.command(name="pause", aliases=["pa"],description="現在一時停止している曲を再開します")
    async def _pause(self, ctx: commands.Context):
        """`誰でも`"""
        if ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction("⏯")

    @commands.command(name="resume", aliases=["re", "res"],description="現在一時停止している曲を再開します")
    async def _resume(self, ctx: commands.Context):
        """`誰でも`"""
        if ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction("⏯")

    @commands.command(name="stop",description="曲の再生を停止し、キューをクリアします")
    async def _stop(self, ctx: commands.Context):
        """`誰でも`"""
        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction("⏹")

    @commands.command(name="skip", aliases=["s", "sk"],description="曲をスキップします")
    async def _skip(self, ctx: commands.Context):
        """`誰でも`"""
        if not ctx.voice_state.is_playing:
            return await ctx.send("現在、音楽を再生していません")

        voter = ctx.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction("⏭")
            ctx.voice_state.loop = False
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 1:
                await ctx.message.add_reaction("⏭")
                ctx.voice_state.loop = False
                ctx.voice_state.skip()
            else:
                await ctx.send(f"Skip vote added, currently at **{total_votes}/1**")

        else:
            await ctx.send("You have already voted to skip this song.")

    @commands.command(name="queue", aliases=["q"],description="キューの中身を確認します")
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """
        `誰でも`
        """
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        items_per_page = 10
        # -(-3//2) == 2, just gets the ceil
        pages = -(-len(ctx.voice_state.songs) // items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ""
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += f"`{i + 1}.` [**{song.source.title}**]({song.source.url})\n"

        embed = discord.Embed(
            description=f"**{len(ctx.voice_state.songs)} tracks:**\n\n{queue}"
        ).set_footer(text=f"Viewing page {page}/{pages}")
        await ctx.send(embed=embed)

    @commands.command(name="shuffle",description="キューの曲をシャッフルします")
    async def _shuffle(self, ctx: commands.Context):
        """`誰でも`"""
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction("✅")

    @commands.command(name="remove",description="指定した曲をキューから消します")
    async def _remove(self, ctx: commands.Context, index: int):
        """
        `誰でも`
        """
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction("✅")

    @commands.command(name="loop",description="曲をループ状態にします")
    async def _loop(self, ctx: commands.Context):
        """`誰でも`"""
        if not ctx.voice_state.is_playing:
            return await ctx.send("Nothing being played at the moment.")

        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction("✅")

    @commands.command(name="play",description="指定した曲を再生します")
    async def _play(self, ctx: commands.Context, *, search: str):
        """
        `誰でも`
        """
        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
            except YTDLError:
                pass
            else:
                if not ctx.voice_state.voice:
                    await ctx.invoke(self._join)

                song = Song(source)
                await ctx.voice_state.songs.put(song)
                await ctx.send(f"Enqueued {source}")

    @commands.command(name="search",description="検索した曲をキューに追加します")
    async def _search(self, ctx: commands.Context, *, search: str):
        """
        `誰でも`
        """
        async with ctx.typing():
            try:
                source = await YTDLSource.search_source(ctx, search, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send(f"An error occurred while processing this request: {e}")
            else:
                if source == "sel_invalid":
                    await ctx.send("Invalid selection")
                elif source == "cancel":
                    await ctx.send(":white_check_mark:")
                elif source == "timeout":
                    await ctx.send(":alarm_clock: **Time's up bud**")
                else:
                    if not ctx.voice_state.voice:
                        await ctx.invoke(self._join)

                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send(f"Enqueued {source}")

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError("You are not connected to any voice channel.")

        if ctx.voice_client and ctx.voice_client.channel != ctx.author.voice.channel:
            raise commands.CommandError("Bot is already in a voice channel.")

    @commands.command(description="指定した曲の歌詞を表示します")
    async def lyric(self, ctx, *, title=None):
        """`誰でも`"""
        if not title:
            title = ctx.voice_state.current.ret_lyric()
        lyrics = await api.get_lyrics(str(title))
        embed = discord.Embed(title=f"{lyrics.title} - {lyrics.author}", description=lyrics.lyrics, url=lyrics.link,
                              timestamp=ctx.message.created_at)
        try:
            try:
                embed.set_thumbnail(url=lyrics.thumbnail)
                await ctx.send(embed=embed)
            except:
                await ctx.send(embed=embed)
        except:
            try:
                await ctx.send("I tried to send an embed, but it was too long. Here is the text file.")
                if lyrics.title != "requirements" and lyrics.title != "runtime" and lyrics.title != "main":
                    lyrics.save()
                    with open(f"{lyrics.title}.txt") as fp:
                        await ctx.send(file=discord.File(fp))
                    os.remove(f"{lyrics.title}.txt")
            except:
                try:
                    if lyrics.title != "requirements" and lyrics.title != "runtime" and lyrics.title != "main":
                        os.remove(f"{lyrics.title}.txt")
                    await ctx.send("Hmmm, I was unable to send an embed, and I couldn't send a file either.")
                except:
                    await ctx.send("Hmmm, I was unable to send an embed, and I couldn't send a file either.")

def setup(bot: commands.Bot) -> None:
    """Starts music cog."""
    bot.add_cog(music(bot))