import discord
from discord.ext import commands
import yt_dlp
import asyncio
import random

# 인텐트 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# yt-dlp 설정 (사운드클라우드 기본 검색 적용)
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'scsearch',  # 기본 검색을 사운드클라우드로 고정
    'source_address': '0.0.0.0',
    'extractor_args': {
        'youtube': {
            'player_client': ['web_embedded', 'tv', 'mweb']
        }
    }
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# 대기열(Queue) 딕셔너리
music_queues = {}

async def play_next(ctx):
    """현재 곡이 끝나면 다음 곡(또는 랜덤 곡)을 재생하는 함수"""
    if not ctx.voice_client:
        return

    # 1. 대기열에 노래가 있는 경우 (신청곡 재생)
    if ctx.guild.id in music_queues and len(music_queues[ctx.guild.id]) > 0:
        next_url = music_queues[ctx.guild.id].pop(0)
        try:
            player = await YTDLSource.from_url(next_url, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: bot.loop.create_task(play_next(ctx)))
            await ctx.send(f'▶️ 다음 신청곡 재생 중: **{player.title}**')
        except Exception as e:
            await ctx.send("노래를 불러오는 중 오류가 발생하여 다음 곡으로 넘어갑니다.")
            await bot.loop.create_task(play_next(ctx))

    # 2. 대기열이 비어있는 경우 (사운드클라우드 랜덤 재생)
    else:
        await ctx.send("🎶 재생목록이 끝났습니다! 사운드클라우드에서 랜덤으로 음악을 추천해 드릴게요.")
        try:
            # 유튜브 접근을 원천 차단하고 사운드클라우드(scsearch)에서만 검색하도록 강제 지정
            keywords = ['kpop top', '아이유', '뉴진스', '에스파', '발라드', '인디음악']
            search_query = f"scsearch15:{random.choice(keywords)}"
            
            data = await bot.loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=False))

            if 'entries' in data and len(data['entries']) > 0:
                valid_entries = [e for e in data['entries'] if e is not None]
                if valid_entries:
                    random_entry = random.choice(valid_entries)
                    random_url = random_entry['url']

                    player = await YTDLSource.from_url(random_url, loop=bot.loop, stream=True)
                    ctx.voice_client.play(player, after=lambda e: bot.loop.create_task(play_next(ctx)))
                    await ctx.send(f'🔀 랜덤 추천 재생 중: **{player.title}**')
            else:
                await ctx.send("랜덤 곡을 찾을 수 없어 봇이 퇴장합니다.")
                await ctx.voice_client.disconnect()
        except Exception as e:
            print(f"랜덤 재생 오류: {e}")
            await ctx.send("랜덤 곡을 불러오는 중 오류가 발생하여 퇴장합니다.")
            if ctx.voice_client:
                await ctx.voice_client.disconnect()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def 재생(ctx, *, url):
    """(노래가 없을 때) 처음 음악을 재생시킵니다."""
    if not ctx.author.voice:
        return await ctx.send("먼저 음성 채널에 접속해 주세요!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
        await ctx.send("✅ 음성 채널에 입장했습니다.")

    if ctx.voice_client.is_playing():
        return await ctx.send("현재 노래가 재생 중입니다. 신청곡을 예약하려면 `!추가 [노래제목/링크]` 명령어를 사용해 주세요!")

    if ctx.guild.id not in music_queues:
        music_queues[ctx.guild.id] = []

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: bot.loop.create_task(play_next(ctx)))
            await ctx.send(f'▶️ 재생 중: **{player.title}**')
        except Exception as e:
            await ctx.send(f"오류가 발생했습니다: {e}")

@bot.command()
async def 추가(ctx, *, url):
    """현재 재생 중인 노래 뒤에 신청곡을 예약합니다."""
    if not ctx.voice_client or not ctx.voice_client.is_playing():
        return await ctx.send("현재 봇이 노래를 부르고 있지 않습니다. `!재생` 명령어로 먼저 노래를 시작해 주세요!")

    if ctx.guild.id not in music_queues:
        music_queues[ctx.guild.id] = []

    music_queues[ctx.guild.id].append(url)
    await ctx.send(f'📝 재생목록에 추가되었습니다: **{url}**')

@bot.command()
async def 재생목록(ctx):
    """현재 대기 중인 신청곡 목록을 보여줍니다."""
    if ctx.guild.id not in music_queues or not music_queues[ctx.guild.id]:
        return await ctx.send("📜 현재 재생목록이 텅 비어있습니다. (랜덤 재생 대기 중)")

    queue_text = "**[현재 대기 중인 신청곡 목록]**\n"
    for i, song in enumerate(music_queues[ctx.guild.id]):
        queue_text += f"{i + 1}. {song}\n"
    
    await ctx.send(queue_text)

@bot.command()
async def 스킵(ctx):
    """현재 재생 중인 곡을 넘깁니다."""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ 곡을 스킵했습니다!")
    else:
        await ctx.send("현재 재생 중인 곡이 없습니다.")

@bot.command()
async def 퇴장(ctx):
    """재생을 강제로 멈추고 대기열을 비운 뒤 퇴장합니다."""
    if ctx.voice_client:
        if ctx.guild.id in music_queues:
            music_queues[ctx.guild.id].clear()
            
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("모든 재생목록을 비우고 퇴장합니다. ✋")
    else:
        await ctx.send("봇이 음성 채널에 접속해 있지 않습니다.")

bot.run(__import__("os").environ["DISCORD_BOT_TOKEN"])

