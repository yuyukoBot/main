import datetime

import discord
from discord.ext import commands
from googleapiclient.discovery import build
import os
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
import youtube_dl
from youtube_dl import YoutubeDL


ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ytdl_download_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.mp3',
    'reactrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addreacses cause issues sometimes
    'source_addreacs': '0.0.0.0',
    'output': r'youtube-dl',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
        }]
}

stim = {
    'default_search': 'auto',
    "ignoreerrors": True,
    'quiet': True,
    "no_warnings": True,
    "simulate": True,  # do not keep the video files
    "nooverwrites": True,
    "keepvideo": False,
    "noplaylist": True,
    "skip_download": False,
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}


ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)

ffmpeg_options = {
    'options': '-vn',

}

class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""

class Downloader(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get("url")
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration')
        self.views = data.get('view_count')
        self.playlist = {}

    @classmethod
    async def video_url(cls, url, ytdl, *, loop=None, stream=False):
        """
        Download the song file and data
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        song_list = {'queue': []}
        if 'entries' in data:
            if len(data['entries']) > 1:
                playlist_titles = [title['title'] for title in data['entries']]
                song_list = {'queue': playlist_titles}
                song_list['queue'].pop(0)

            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data), song_list

    async def get_info(self, url):
        """
        Get the info of the next song by not downloading the actual file but just the data of song/query
        """
        yt = youtube_dl.YoutubeDL(stim)
        down = yt.extract_info(url, download=False)
        data1 = {'queue': []}
        if 'entries' in down:
            if len(down['entries']) > 1:
                playlist_titles = [title['title'] for title in down['entries']]
                data1 = {'title': down['title'], 'queue': playlist_titles}

            down = down['entries'][0]['title']

        return down, data1


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester
        self.thumbnail = data.get('thumbnail')

        self.duration = data.get('duration')
        if self.duration is None:
            self.duration = 0

        self.uploader = data.get('uploader')

        if self.uploader is None:
            self.uploader = "Unknown uploader"


        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f'```ini\n[{data["title"]} をキューに追加しました]\n```')

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer(commands.Cog):
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        self.bot.color = 0x5d00ff

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.bot.color = 0x5d00ff

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['join'],description="botをボイスチャンネルに接続します")
    async def connect_(self, ctx):
        """`誰でも`"""
        try:
            channel = ctx.author.voice.channel
        except AttributeError:
            raise InvalidVoiceChannel('No channel to join.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

        await ctx.send(f'Connected to: **{channel}**', )

    @commands.command(name='play', aliases=['sing'],description="指定した曲を再生します")
    async def play_(self, ctx, *, search: str):
        """`誰でも`"""
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)

    @commands.command(name='pause',description="現在再生中の曲を一時停止します。")
    async def pause_(self, ctx):
        """`誰でも`"""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('現在何も再生されていません')
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f'`{ctx.author}`さんが曲を一時停止しました')

    @commands.command(name='resume',description="現在一時停止している曲を再開します")
    async def resume_(self, ctx):
        """`誰でも`"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('現在何も再生されていません', )
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f'`{ctx.author}`さんが一時停止を解除しました')

    @commands.command(name='skip',description="再生中の曲をスキップします")
    async def skip_(self, ctx):
        """`誰でも`"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('何も再生されてません')

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f'`{ctx.author}`をスキップしました')

    @commands.command(name='queue', aliases=['q', 'playlist'],description="queueの中身を確認します")
    async def queue_info(self, ctx):
        """`誰でも`"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('ボイスチャンネルに接続されていません')

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('現在、キューに入れられている曲はありません')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f' 次の曲{len(upcoming)}', description=fmt,color=self.bot.color)

        await ctx.send(embed=embed)



    @commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'],description="再生中の曲を表示します")
    async def now_playing_(self, ctx):
        """`誰でも`"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('ボイスチャンネルに接続していません', )

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('現在何も再生されていません')

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        e = discord.Embed(title="今再生してる曲",color=self.bot.color)
        e.add_field(name="再生されてる曲",value=f"{vc.source.title}({vc.source.uploader})")
        e.add_field(name="リクエストした人",value=vc.source.requester)
        e.add_field(name="url",value=vc.source.web_url)
        e.add_field(name="再生時間", value=f"**{datetime.timedelta(seconds=vc.source.duration)}**")
        player.np = await ctx.send(embed=e)

    @commands.command()
    async def search(self, ctx, *, search):
        async with ctx.typing():
            results = ytdl.extract_info(f'ytsearch10:{search}', download=False)['entries']
            await ctx.send(
                embed=discord.Embed(
                    description='\n'.join(
                        [f'[{video["title"]}]({video["webpage_url"]}) by {video["uploader"]} ({video["duration"]}' for video in results])
                )
            )

    @commands.command(name="repeat",description="曲をリピートします")
    async def repeat(self, msg):
        """
        `誰でも`
        """
        if msg.guild.id in self.player:
            if msg.voice_client.is_playing() is True:
                if self.player[msg.guild.id]['repeat'] is True:
                    self.player[msg.guild.id]['repeat'] = False
                    return await msg.message.add_reaction(emoji='✅')

                self.player[msg.guild.id]['repeat'] = True
                return await msg.message.add_reaction(emoji='✅')

            return await msg.send("No audio currently playing")
        return await msg.send("Bot not in voice channel or playing music")

    @commands.command(name='volume', aliases=['vol'],description="音量を変更します")
    async def change_volume(self, ctx, *, vol: float):
        """`誰でも`
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('ボイスチャンネルに接続していません', )

        if not 0 < vol < 101:
            return await ctx.send('1から100までの値を入力してください')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f'`{ctx.author}`さんが **{vol}%**にセットしました')

    @commands.command(name='stop', aliases=['leave'],description="queueの再生をやめます")
    async def stop_(self, ctx):
        """`誰でも`"""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('現在何も再生されていません')

        await self.cleanup(ctx.guild)

    @commands.command(brief='Download songs', description='指定した曲をダウンロードします')
    async def download(self, ctx, *, song):
        """
        `誰でも`
        """
        try:
            with youtube_dl.YoutubeDL(ytdl_download_format_options) as ydl:
                if "https://www.youtube.com/" in song:
                    download = ydl.extract_info(song, True)
                else:
                    infosearched = ydl.extract_info(
                        "ytsearch:" + song, False)
                    download = ydl.extract_info(
                        infosearched['entries'][0]['webpage_url'], True)
                filename = ydl.prepare_filename(download)
                embed = discord.Embed(
                    title='ダウンロードの準備ができました',
                    description="ファイルがアップロードされている間、しばらくお待ちください")
                await ctx.send(embed=embed, delete_after=30)
                await ctx.send(file=discord.File(filename))
                os.remove(filename)
        except (youtube_dl.utils.ExtractorError, youtube_dl.utils.DownloadError):
            embed = discord.Embed(title="ダウンロードできませんでした", description=("Song:" + song),color=self.bot.color)
            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Music(client))