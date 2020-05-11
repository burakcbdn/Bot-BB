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


@bot.command(name="selam", help="Greets the user.")
async def greet_the_user(ctx):
    await send_embedded(ctx, f"Selam, {ctx.message.author.name}!")


@bot.command(name="github", help="opens burakcbdn github profile on browser.")
async def launch_github(ctx):
    webbrowser.open("www.github.com/burakcbdn")


@bot.command(name="translate", help="translates word from source language to destination language.")
async def translate(ctx, src, dest, word):
    if src not in googletrans.LANGCODES.values():
        await send_embedded(ctx, "hatalı kaynak dil kodu!")
        return

    if dest not in googletrans.LANGCODES.values():
        await end_embedded(ctx, "hatalı hedef dil kodu!")
        return

    translator = googletrans.Translator()
    translated = translator.translate(word, src=src, dest=dest)
    await nd_embedded(ctx, f" {word} => {translated.text}")


@bot.command(name="langcodes", help="lists all the available language codes for translate.")
async def langcodes(ctx):
    languages = googletrans.LANGCODES.keys()
    codes = googletrans.LANGCODES.values()

    pairs = []

    for language in googletrans.LANGCODES.keys():
        code = googletrans.LANGCODES[language]

        pairs.append(f"- {language} => {code}")

    pair_list = "\n".join(pairs)
    await send_embedded(ctx, pair_list)


@bot.command(name="roll", help="Rolls a dice.")
async def roll(ctx):
    dice = random.randint(0, 6)
    await send_embedded(ctx, f"gelen zar: {dice}")
    dice = None


@bot.command(name="members", help="Lists members in the server.")
async def members(ctx):
    member_names = []
    for member in ctx.guild.members:
        member_names.append(member.name)

    member_list = "\n".join(member_names)
    await send_embedded(ctx, member_list)

@bot.command(name="bot-bb", help="Gives information about Bot-BB")
async def bot_bb(ctx):
    await send_embedded(ctx, "Bot-BB Burak Cabadan ve Billur Baş tarafından yapılmakta olan Discord botudur")


@bot.command(name="covid", help="Shows statistics about covid in country.")
async def display_covid(ctx, country=None):
    try:
        info = getCovidInfo(country)
        tC = info["totalConfirmed"]
        tD = info["totalDeath"]
        await send_embedded(ctx, f"-{country}- \n  toplam vaka: {tC} \n  toplam ölüm: {tD}")
    except:
        await send_embedded(ctx, "Ülke ismi belirtmediniz (!covid turkey)")


@bot.command(name="join", help="Moves bot to users voice channel.")
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

    await send_embedded(ctx, f"'{channel}' ses kanalına bağlandım")


@bot.command(name="play", help="Plays audio in the voice channel.")
async def play(ctx, url: str, *words):

    channel = ctx.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if not (voice and voice.is_connected()):
        await join(ctx)


    for word in words:
        if word == "-":
            url = url + word
        url = url + "_" + word


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
                await ctx.send_embedded(ctx, "Bu da sonuncusuydu.")
                queues.clear()
                return
            main_path = os.path.dirname(os.path.realpath(__file__)) 
            q_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_audio)

            if length != 0:
                print("playing next song")
                await send_embedded(ctx, "Sıradaki ses çalınıyor.")
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
        await send_embedded(ctx, "Maalesef aynı anda iki ses çalamam.")
        return

    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("old queue folder removed")
            shutil.rmtree(Queue_folder)
    except:
        print("no old queue folder")


    await send_embedded(ctx, "Sahneye hazırlanıyorum. Beklemelisin :)")

    voice = get(bot.voice_clients, guild=ctx.guild)
    ydl_options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'

        }]
    }

    try:
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            print("downloading audio")
            ydl.download([url])
    except:
        print("Unsupported url type. Trying Spotify.")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -f" + '"' + c_path + '"' + " -s " + url)
    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            os.rename(file, 'audio.mp3')

    voice.play(discord.FFmpegPCMAudio('audio.mp3'), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    nname = name.rsplit('-')

    await send_embedded(ctx, f"'{nname[0] + nname[1]}' çalınıyor")


@bot.command(name="leave", help = "Bot-BB leaves current voice channel.")
async def leave(ctx):
    channel = ctx.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"the bot has left channel {channel}")
        await send_embedded(ctx, f"'{channel}' ses kanalından ayrıldım")

    else:
        print("bot is not in any channel")
        await send_embedded(ctx, "Herhangi bir kanalda değilim ki :(")


@bot.command(name="pause", help="Pauses currently playing audio.")
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.pause()
        await send_embedded(ctx, "Ses durduruldu.")

    else:
        await send_embedded(ctx, "Ortalık zaten sessiz.")


@bot.command(name="resume", help="Resumes paused audio.")
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        voice.resume()
        await send_embedded(ctx, "Ses tekrar yürütülüyor.")

    else:
        await send_embedded(ctx, "Ses zaten yürütülüyor")


@bot.command(name="stop", help="Stops currently playing audio.")
async def stop(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    if voice and voice.is_playing():
        voice.stop()
        await send_embedded(ctx, "Ses durduruldu")

    else:
        await send_embedded(ctx, "Ortalık zaten sessiz.")


queues = {}

@bot.command(name="queue",help="Adds songs to queue.")
async def queue(ctx, url: str, *words):

    for word in words:
        if word == "-":
            url = url + word
        url = url + "_" + word

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

    try:
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            print("downloading audio")
            ydl.download([url])
    except:
        print("Unsupported url type. Trying Spotify.")
        q_path = os.path.abspath(os.path.realpath("Queue"))
        system(f"spotdl -ff audio{q_num} -f "+ '"' + q_path + '"' + " -s "+url)
    await send_embedded(ctx, f"ses sıraya eklendi!")    

    print("sond added to queue")


bot.run(TOKEN)
