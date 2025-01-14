import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {'options':'-vn'}
YDL_OPTIONS = {'format':'bestaudio','noplaylist': True}

class MusicBot(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.queue = []

    @commands.command()
    async def play(self,ctx,search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        #print("test1")
        if not voice_channel:
            return await ctx.send("join a voice chanel")
        if not ctx.voice_client:
            print("trying to connect")
            try:
                await voice_channel.connect()
                print("connected")
            except Exception as e:
                print("error "+e)
            
        #print("test2")
        async with ctx.typing():
            #print("test3")
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download = False)
                if 'entries' in info:
                    #print("test4")
                    info = info['entries'][0]
                    url =  info['url']
                    title = info['title']
                    self.queue.append((url,title))
                    await ctx.send(f"Added to queue: **{title}**")
        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self,ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source,after = lambda _:self.client.loop.create_task(self.play_next(ctx)))
            await ctx.send(f"now playing: **{title}**")
        elif not ctx.voice_client.is_playing:
            await ctx.send("added to queue")

    @commands.command()
    async def skip(self,ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("skipped")

async def main():
    client = commands.Bot(command_prefix = '!',intents = intents)
    await client.add_cog(MusicBot(client))
    await client.start('copy your discord id here')#leave the quotes and remember not to let the token out of your hands!

asyncio.run(main())