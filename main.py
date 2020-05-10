import os
import random
import webbrowser
import googletrans
import requests
import youtube_dl
import discord
import shutil
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from os import system

load_dotenv()

TOKEN = os.environ.get('BOT_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(command_prefix="!")


async def send_embedded(ctx, content):
    embed = discord.Embed(color=0x00ff00, description=content)
    await ctx.send(embed=embed)


def getCovidInfo(country):
    response = requests.get("https://api.covid19api.com/summary")

    if response.status_code == 200:
        countries = response.json()["Countries"]
        country = country
        for data in countries:
            if data["Country"].lower() == country.lower():
                totalConfirmed = data["TotalConfirmed"]
                totalDeath = data["TotalDeaths"]
                return {"totalConfirmed": totalConfirmed, "totalDeath": totalDeath}

    else:
        return


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to server')


@bot.command(name="selam", help="Sizi selamlar")
async def greet_the_user(ctx):
    embed = discord.Embed(color=0x00ff00, description=f"Selam, {ctx.message.author.name}!")
    await ctx.send(embed=embed)


@bot.command(name="github", help="burakcbdn github profilini açar")
async def launch_github(ctx):
    webbrowser.open("www.github.com/burakcbdn")


@bot.command(name="translate", help="belirlenen dilden diğer dile çeviri yapar => (!translate en tr Hello)")
async def translate(ctx, src, dest, word):
    if src not in googletrans.LANGCODES.values():
        embed = discord.Embed(color=0x00ff00, description="hatalı kaynak dil kodu!")
        await ctx.send(embed=embed)
        return

    if dest not in googletrans.LANGCODES.values():
        embed = discord.Embed(color=0x00ff00, description="hatalı hedef dil kodu!")
        await ctx.send(embed=embed)
        return

    translator = googletrans.Translator()
    translated = translator.translate(word, src=src, dest=dest)
    embed = discord.Embed(color=0x00ff00, description=f" {word} => {translated.text}")
    await ctx.send(embed=embed)


@bot.command(name="langcodes", help="çeviri yapmak için desteklenen dil kodlarını listeler")
async def langcodes(ctx):
    languages = googletrans.LANGCODES.keys()
    codes = googletrans.LANGCODES.values()

    pairs = []

    for language in googletrans.LANGCODES.keys():
        code = googletrans.LANGCODES[language]

        pairs.append(f"- {language} => {code}")

    pair_list = "\n".join(pairs)
    embed = discord.Embed(color=0x00ff00, description=pair_list)
    await ctx.send(embed=embed)


@bot.command(name="roll", help="Zar atar")
async def roll(ctx):
    dice = random.randint(0, 6)
    embed = discord.Embed(color=0x00ff00, description=f"gelen zar: {dice}")
    await ctx.send(embed=embed)
    dice = None


@bot.command(name="members", help="Sunucudaki üyeleri listeler")
async def members(ctx):
    member_names = []
    for member in ctx.guild.members:
        member_names.append(member.name)

    member_list = "\n".join(member_names)
    embed = discord.Embed(color=0x00ff00, description=member_list)
    await ctx.send(embed=embed)


@bot.command(name="bot-bb", help="Bot-BB hakkında bilgi verir")
async def bot_bb(ctx):
    embed = discord.Embed(color=0x00ff00,
                          description="Bot-BB Burak Cabadan ve Billur Baş tarafından yapılmakta olan Discord botudur")
    await ctx.send(embed=embed)


@bot.command(name="covid", help="seçilen ülkenin covid-19 istatistiklerini gösterir")
async def display_covid(ctx, country=None):
    try:
        info = getCovidInfo(country)
        tC = info["totalConfirmed"]
        tD = info["totalDeath"]
        embed = discord.Embed(color=0x00ff00, description=f"-{country}- \n  toplam vaka: {tC} \n  toplam ölüm: {tD}")
        await ctx.send(embed=embed)
    except:
        embed = discord.Embed(color=0x00ff00, description="Ülke ismi belirtmediniz (!covid turkey)")
        await ctx.send(embed=embed)


@bot.command(name="join")
async def join(ctx):
        # joining the channel
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)

    else:
        voice = await channel.connect()
        print(f"the bot has connected to {channel} \n")

    embed = discord.Embed(color=0x00ff00, description=f"'{channel}' ses kanalına bağlandım")
    await ctx.send(embed=embed)


@bot.command(name="play")
async def play(ctx, url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_audio = os.listdir(DIR)[0]

            except:
                print("queue is empty")
                queues.clear()
                return
            main_path = os.path.dirname(os.path.realpath(__file__)) 
            q_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_audio)

            if length != 0:
                print("playing next song")
                is_song_exist = os.path.isfile("audio.mp3")
                if is_song_exist:
                    os.remove("audio.mp3")
                shutil.move(q_path, main_path)

                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, "audio.mp3")

                voice.play(discord.FFmpegPCMAudio('audio.mp3'), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07
            else: 
                queues.clear()
                return
        else:
            queues.clear()
            print("no audio in queue")    


    # playing audio
    is_song_exist = os.path.isfile("audio.mp3")
    try:
        if is_song_exist:
            os.remove("audio.mp3")
            queues.clear()
            print("old file removed")

    except PermissionError:
        embed = discord.Embed(color=0x00ff00, description="Maalesef aynı anda iki ses çalamam.")
        await ctx.send(embed=embed)
        return

    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("old queue folder removed")
            shutil.rmtree(Queue_folder)
    except:
        print("no old queue folder")


    embed = discord.Embed(color=0x00ff00, description="Sahneye hazırlanıyorum. Beklemelisin :)")
    await ctx.send(embed=embed)

    voice = get(bot.voice_clients, guild=ctx.guild)
    ydl_options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'

        }]
    }

    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        print("downloading audio")
        ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            os.rename(file, 'audio.mp3')

    voice.play(discord.FFmpegPCMAudio('audio.mp3'), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    name = name.rsplit('-')

    embed = discord.Embed(color=0x00ff00, description=f"'{name[0] + name[1]}' çalınıyor")
    await ctx.send(embed=embed)


@bot.command(name="leave")
async def leave(ctx):
    channel = ctx.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"the bot has left channel {channel}")
        embed = discord.Embed(color=0x00ff00, description=f"'{channel}' ses kanalından ayrıldım")
        await ctx.send(embed=embed)

    else:
        print("bot is not in any channel")
        embed = discord.Embed(color=0x00ff00, description="Herhangi bir kanalda değilim ki :(")
        await ctx.send(embed=embed)


@bot.command(name="pause")
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
        await send_embedded(ctx, "Ses durduruldu.")

    else:
        await send_embedded(ctx, "Ortalık zaten sessiz.")


@bot.command(name="resume")
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
        await send_embedded(ctx, "Ses tekrar yürütülüyor.")

    else:
        await send_embedded(ctx, "Ses zaten yürütülüyor")


<<<<<<< HEAD
@bot.command(name="stop")
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    if voice and voice.is_playing():
        voice.stop()
        await send_embedded(ctx, "Ses durduruldu")

    else:
        await send_embedded(ctx, "Ortalık zaten sessiz.")


queues = {}

@bot.command(name="queue")
async def queue(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")

    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True 
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\\audio{q_num}.%(ext)s")

    ydl_options = {
    'format': 'bestaudio/best',
    'outtmpl':queue_path,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'

        }]
    }

    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        print("downloading audio")
        ydl.download([url])

    await send_embedded(ctx, f"ses{q_num} sıraya eklendi!")    

    print("sond added to queue")


=======
>>>>>>> parent of 8df2d23... !stop added
bot.run(TOKEN)
