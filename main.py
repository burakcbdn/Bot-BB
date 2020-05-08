import os
import random
import webbrowser
import googletrans
import requests
import youtube_dl
import discord
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to server')


@bot.command(name="selam", help="Sizi selamlar")
async def greet_the_user(ctx):
    await ctx.send(f"Selam, {ctx.message.author.name}!")


@bot.command(name="translate", help="belirlenen dilden diğer dile çeviri yapar => (!translate en tr Hello)")
async def translate(ctx, src, dest, word):
    if src not in googletrans.LANGCODES.values():
        await ctx.send("hatalı kaynak dil kodu!")
        return

    if dest not in googletrans.LANGCODES.values():
        await ctx.send("hatalı hedef dil kodu!")
        return

    translator = googletrans.Translator()
    translated = translator.translate(word, src=src, dest=dest)
    await ctx.send(f" {word} => {translated.text}")


@bot.command(name="langcodes", help="çeviri yapmak için desteklenen dil kodlarını listeler")
async def langcodes(ctx):
    languages = googletrans.LANGCODES.keys()
    codes = googletrans.LANGCODES.values()

    pairs = []

    for language in googletrans.LANGCODES.keys():
        code = googletrans.LANGCODES[language]

        pairs.append(f"- {language} => {code}")

    pair_list = "\n".join(pairs)
    await ctx.send(pair_list)


@bot.command(name="roll", help="Zar atar")
async def roll(ctx):
    dice = random.randint(0, 6)
    await ctx.send(f"gelen zar: {dice}")
    dice = None


@bot.command(name="members", help="Sunucudaki üyeleri listeler")
async def members(ctx):
    member_names = []
    for member in ctx.guild.members:
        member_names.append(member.name)

    member_list = "\n".join(member_names)
    await ctx.send(member_list)

@bot.command(name="bot-bb", help = "Bot-BB hakkında bilgi verir")
async def bot_bb(ctx):
    await ctx.send("Bot-BB Burak Cabadan ve Billur Baş tarafından yapılmakta olan Discord botudur")
    

@bot.command(name="covid", help="seçilen ülkenin covid-19 istatistiklerini gösterir")
async def display_covid(ctx, country = None):
    try:
        info = getCovidInfo(country)
        tC = info["totalConfirmed"]
        tD = info["totalDeath"]
        await ctx.send(f"-{country}- \n  toplam vaka: {tC} \n  toplam ölüm: {tD}")
    except:
        await ctx.send("Ülke ismi belirtmediniz (!covid turkey)")


def getCovidInfo(country):
    response = requests.get("https://api.covid19api.com/summary")

    if response.status_code == 200:
        countries = response.json()["Countries"]
        country = country
        for data in countries:
            if data["Country"].lower()==country.lower():
                totalConfirmed = data["TotalConfirmed"]
                totalDeath = data["TotalDeaths"]
                return {"totalConfirmed":totalConfirmed, "totalDeath": totalDeath}
        
    else:
        return


@bot.command(name="play")
async def play(ctx, url: str):


    #joining the channel
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)

    else:
        voice = await channel.connect()
        print(f"the bot has connected to {channel} \n")

    await ctx.send(f"'{channel}' ses kanalına bağlandım")

    #playing audio

    is_song_exist = os.path.isfile("audio.mp3")
    try:
        if is_song_exist:
            os.remove("audio.mp3")
            print("old file removed")

    except PermissionError:
        await ctx.send("Zaten bir ses çalıyor.")
        return

    await ctx.send("Sahneye hazırlanıyorum. Beklemelisin :)")

    ydl_options = {
        'format':'bestaudio/best',
        'postprocessors': [{
            'key':'FFmpegExtractAudio',
            'preferredcodec':'mp3',
            'preferredquality':'192'

        }]
    }

    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        print("downloading audio")
        ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            name = file
            os.rename(file, 'audio.mp3')

    voice.play(discord.FFmpegPCMAudio('audio.mp3'), after=lambda e : print(f"{name} has finished playing"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07
    name = name.rsplit('-', 2)
    await ctx.send(f"'{name[0]}' çalınıyor")
    
    
@bot.command(name="stop")
async def stop(ctx):
    channel = ctx.author.voice.channel
    voice = get(bot.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"the bot has left channel {channel}")
        await ctx.send(f"'{channel}' ses kanalından ayrıldım")

    else:
        print("bot is not in any channel")
        await ctx.send("Herhangi bir kanalda değilim ki :(")


bot.run(TOKEN)
