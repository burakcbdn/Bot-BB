import os
import random
import webbrowser
import googletrans
import requests
import youtube_dl
import discord
import shutil
import sqlite3
import platform
from loop_controller import LoopController
from os_controller import OsController
from message_sender import send_embedded
from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv
from os import system

load_dotenv()

slash_prefix = ""

TOKEN = os.environ.get('BOT_TOKEN')
bot = commands.Bot(command_prefix="!")

DIR = os.path.dirname(__file__)

db = sqlite3.connect(os.path.join(DIR, "SongTracker.db"))  # connecting to DB if this file is not there it will create it
SQL = db.cursor()

loopController = LoopController()
osController = OsController()

slash_prefix = osController.slash_prefix

queues = {}
queue_path = ""

def main():
    bot.run(TOKEN)

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


@bot.command(name="github", help="Burak Cabadan Github")
async def launch_github(ctx):
    await send_embedded(ctx, "Burak Cabadan Github: \n https://www.github.com/burakcbdn")


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
    await send_embedded(ctx, f" {word} => {translated.text}")


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
    await send_embedded(ctx, "Bot-BB Burak Cabadan ve Billur Baş tarafından yapılmakta olan Discord botudur.")


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
    ###DATABASE CONNECTION###
    SQL.execute('create table if not exists Music('
            '"Num" integer not null primary key autoincrement, '
            '"Server_ID" integer, '
            '"Server_Name" text, '
            '"Voice_ID" integer, '
            '"Voice_Name" text, '
            '"User_Name" text, '
            '"Next_Queue" integer, '
            '"Queue_Name" text, '
            '"Song_Name" text'
            ')')
    server_name = str(ctx.guild)
    server_id = ctx.guild.id
    SQL.execute(f'delete from music where Server_ID ="{server_id}" and Server_Name = "{server_name}"')
    db.commit()
    user_name = str(ctx.message.author)
    queue_name = f"Queue#{server_id}"
    song_name = f"Song#{server_id}"
    channel_id = ctx.message.author.voice.channel.id
    channel_name = str(ctx.message.author.voice.channel)
    queue_num = 1
    SQL.execute('insert into Music(Server_ID, Server_Name, Voice_ID, Voice_Name, User_Name, Next_Queue, Queue_Name, Song_Name) values(?,?,?,?,?,?,?,?)',
                (server_id, server_name, channel_id, channel_name, user_name, queue_num, queue_name, song_name))
    db.commit()
    #########################


    # joining the channel
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice is not None:
        return await voice.move_to(channel)

    await channel.connect()

    await send_embedded(ctx, f"'{channel}' ses kanalına bağlandım")


@bot.command(name="play", help="Plays audio in the voice channel.")
async def play(ctx, url: str, *words):

    for word in words:
        if word == "-":
            url = url + word
        url = url + "_" + word

    ###DATABASE ORGANIZING###
    server_name = str(ctx.guild)
    server_id = ctx.guild.id
    channel_id = ctx.message.author.voice.channel.id
    channel_name = str(ctx.message.author.voice.channel)

    channel = ctx.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    if not (voice and voice.is_connected()):
        await join(ctx)

    try:
        SQL.execute(f'select Song_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}" and Voice_ID="{channel_id}" and Voice_Name="{channel_name}"')
        name_song = SQL.fetchone()
        SQL.execute(f'select Server_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
        name_server = SQL.fetchone()
    except:
        pass

    #########################

    await send_embedded(ctx, "Sahneye hazırlanıyorum. Beklemelisin...")
    
    def check_queue(): # burda
        ###DATABASE ORGANIZING###
        DIR = os.path.dirname(__file__)
        db = sqlite3.connect(os.path.join(DIR, "SongTracker.db"))
        SQL = db.cursor()
        SQL.execute(f'select Queue_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
        name_queue = SQL.fetchone()
        SQL.execute(f'select Server_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
        name_server = SQL.fetchone()

        #########################


        Queue_Main = ""
        is_song_exist = False
        Queue_infile = os.path.isdir("./Queues")
        if Queue_infile is True:
            try:
                DIR = os.path.abspath(os.path.realpath("Queues"))
                Queue_Main = os.path.join(DIR, name_queue[0])  # şurda
                length = len(os.listdir(Queue_Main))
                still_q = length - 1
            except:
                pass

            try:
                first_audio = os.listdir(Queue_Main)[0]
                song_num = first_audio.split('-')[0]
            except:
                print("queue is empty.")
                SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
                db.commit()
                return
            main_path = os.path.dirname(os.path.realpath(__file__)) 
            q_path = os.path.abspath(os.path.realpath(Queue_Main) + slash_prefix + first_audio)

            if length != 0:
                print("playing next song.")

                is_song_exist = os.path.isfile(f"{name_song[0]}({name_server[0]}).mp3")
                if is_song_exist:
                    print(loopController.isLoop)
                    if loopController.isLoop == True:
                        try:
                            if is_song_exist:
                                print(f"loop : {loop}")
                                SQL.execute(f'select Queue_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
                                name_queue = SQL.fetchone()
                                SQL.execute(f'select Song_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
                                name_song1 = SQL.fetchone()
                                SQL.execute(f'select Next_Queue from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
                                q_num = SQL.fetchone()

                                queue_path = os.path.abspath(os.path.realpath(Queue_Main) + f"{slash_prefix}{q_num[0]}-{name_song1[0]}({name_server[0]}).mp3")
                                os.rename(f"{name_song1[0]}({name_server[0]}).mp3", queue_path)
                                SQL.execute('update Music set Next_Queue = Next_Queue + 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))

                                db.commit()
                                print("old file removed")

                        except PermissionError:
                            print("sa")
                            return
                    else: pass
                try:
                    os.remove(f"{name_song[0]}({name_server[0]}).mp3")
                except:
                    shutil.move(q_path, main_path)

                for file in os.listdir("./"):
                    if file == f"{song_num}-{name_song[0]}({name_server[0]}).mp3":
                        os.rename(file, f'{name_song[0]}({name_server[0]}).mp3')


                voice.play(discord.FFmpegPCMAudio(f'{name_song[0]}({name_server[0]}).mp3'), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07
            else: 
                SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
                db.commit()                
                return
        else:
            SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
            db.commit()
            print("no audio in queue.")    


    # playing audio
    is_song_exist = os.path.isfile(f"{name_song[0]}({name_server[0]}).mp3")
    try:
        if is_song_exist:
            os.remove(f"{name_song[0]}({name_server[0]}).mp3") # add song to the queue
            SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
            db.commit()
            print("old file removed")

    except PermissionError:
        await send_embedded(ctx, "Maalesef aynı anda iki ses çalamam.")
        return

    SQL.execute(f'select Queue_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
    name_queue = SQL.fetchone()
    Queue_infile = os.path.isdir("./Queues")
    if Queue_infile is True:
        DIR = os.path.abspath(os.path.realpath("Queues"))
        Queue_Main = os.path.join(DIR, name_queue[0])
        Queue_Main_infile = os.path.isdir(Queue_Main)
        if Queue_Main_infile is True:
            print("Removed old queue folder")
            shutil.rmtree(Queue_Main)



    voice = get(bot.voice_clients, guild=ctx.guild)
    song_path = f"./{name_song[0]}({name_server[0]}).mp3"

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
            info = ydl.extract_info(f"ytsearch1:{url}", download=False)
            info_dict = info.get('entries', None)[0]
            print(info_dict)
            video_title = info_dict.get('title', None)
            ydl.download([f"ytsearch1:{url}"])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file,f"{name_song[0]}({name_server[0]}).mp3")
    except:
        print("Unsupported url type. Trying Spotify.")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system(f"spotdl -ff {name_song[0]}({name_server[0]}) -f " + '"' + c_path + '"' + " -s " + url)


    voice.play(discord.FFmpegPCMAudio(f"{name_song[0]}({name_server[0]}).mp3"), after= lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    try:
        await send_embedded(ctx, f"{video_title} çalınıyor")
    except:
        await send_embedded(ctx, "Özel sebeplerden dolayı şarkı ismini gösteremiyorum. Ama çalınıyor şu an.")
        await send_embedded(ctx, "Şaka şaka. Geliştiricim şu anki durumda şarkı ismini gösterecek fonksiyonu geliştiremedi.")


@bot.command(name="leave", help = "Bot-BB leaves current voice channel.")
async def leave(ctx):
    ###DATABASE ORGANIZING###
    server_name = str(ctx.guild)
    server_id = ctx.guild.id
    channel_id = ctx.message.author.voice.channel.id
    channel_name = str(ctx.message.author.voice.channel)
    SQL.execute(f'delete from music where Server_ID ="{server_id}" and Server_Name = "{server_name}" and Voice_ID="{channel_id}" and Voice_Name="{channel_name}"')
    db.commit()
    #########################
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
        await send_embedded(ctx, "Kaldığımız yerden devam.")

    else:
        await send_embedded(ctx, "Ses zaten yürütülüyor.")


@bot.command(name="stop", help="Stops currently playing audio.")
async def stop(ctx):
    ###DATABASE ORGANIZING###
    server_name = str(ctx.guild)
    server_id = ctx.guild.id
    SQL.execute('update Music set Next_Queue = 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
    db.commit()
    SQL.execute(f'select Queue_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
    name_queue = SQL.fetchone()
    #########################


    voice = get(bot.voice_clients, guild=ctx.guild)

    try: 
        queue_infile = os.path.isdir("./Queues")
        if queue_infile:
            DIR = os.path.abspath(os.path.realpath("Queues"))
            Queue_Main = os.path.join(DIR, name_queue[0])
            Queue_Main_infile = os.path.isdir(Queue_Main)
            if Queue_Main_infile is True:
                shutil.rmtree(Queue_Main) 
                os.rmdir(Queue_Main)  
    except:
        pass  

    queues.clear()

    
    if voice and voice.is_playing():
        voice.stop()
        await send_embedded(ctx, "Ses durduruldu.")

    else:
        await send_embedded(ctx, "Ortalık zaten sessiz.")


@bot.command(name="queue",help="Adds songs to queue.")
async def queue(ctx, url: str, *words,):

    for word in words:
        if word == "-":
            url = url + word
        url = url + "_" + word

    ###DATABASE ORGANIZING###
    server_name = str(ctx.guild)
    server_id = ctx.guild.id

    try:
        SQL.execute(f'select Queue_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
        name_queue = SQL.fetchone()
        SQL.execute(f'select Song_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
        name_song = SQL.fetchone()
        SQL.execute(f'select Next_Queue from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
        q_num = SQL.fetchone()
    
    except:
        await ctx.send("Bot herhangi bir ses kanalında değil.")
        return    
    #########################

    

    Queue_infile = os.path.isdir("./Queues")
    if Queue_infile is False:
        os.mkdir("Queues")

    DIR = os.path.abspath(os.path.realpath("Queues"))
    Queue_Main = os.path.join(DIR, name_queue[0])
    Queue_Main_infile = os.path.isdir(Queue_Main)
    if Queue_Main_infile is False:
        os.mkdir(Queue_Main)


    SQL.execute(f'select Server_Name from Music where Server_ID="{server_id}" and Server_Name="{server_name}"')
    name_server = SQL.fetchone()
    queue_path = os.path.abspath(os.path.realpath(Queue_Main) + f"{slash_prefix}{q_num[0]}-{name_song[0]}({name_server[0]}).mp3")



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
            ydl.download([f"ytsearch1:{url}"])
            info = ydl.extract_info(f"ytsearch1:{url}", download=False)
            info_dict = info.get('entries', None)[0]
            video_title = info_dict.get('title', None)
    except:
        Q_DIR = os.path.abspath(os.path.realpath("Queues"))
        Queue_Path = os.path.join(Q_DIR, name_queue[0])
        system(f"spotdl -ff {q_num[0]}-{name_song[0]}({name_server[0]}) -f " + '"' + Queue_Path + '"' + " -s " + song_search)

    try:
        await send_embedded(ctx, f"'{video_title}' sıraya eklendi!")
    except:
        await send_embedded(ctx, "Ses sıraya eklendi.")    

    SQL.execute('update Music set Next_Queue = Next_Queue + 1 where Server_ID = ? and Server_Name = ?', (server_id, server_name))
    db.commit()

    print("song added to queue")
    

@bot.command(name="next", help="Plays the next song in queue.")
async def next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.stop()
        await send_embedded(ctx, "Sıradaki ses oynatılıyor.")

    else:
        await send_embedded(ctx, "Sırada herhangi bir şarkı yok.")


@bot.command(name="volume", help="Changes the volume of the currently playing audio.")
async def volume(ctx, vol:int):
    if ctx.voice_client is None:
        return await send_embedded(ctx, "Ayarlanacak ses yok ki.")

    ctx.voice_client.source.volume = vol / 100

    await send_embedded(ctx, f"Ses seviyesi %{vol} olarak ayarlandı!")


@bot.command(name="loop")
async def loop(ctx):
    if (loopController.isLoop):
        loopController.unLoop()
        await send_embedded(ctx, "Loop kapalı!")
    else: 
        loopController.setLoop()
        await send_embedded(ctx, "Loop açık!")
            

if __name__ == "__main":
    main()
