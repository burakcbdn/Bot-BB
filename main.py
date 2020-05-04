import os
import random
from dotenv import load_dotenv
from discord.ext import commands


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
async def translate(ctx, fr, to, word):
    await ctx.send("Şu anlık çeviri yapamıyorum")


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


bot.run(TOKEN)
