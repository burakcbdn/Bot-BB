import os
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name}(id: {guild.id})')

@client.event
async  def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Merhaba, {member.name}! BBChat Discord sunucusuna hoş geldin.')


client.run(TOKEN)
