import os
import discord
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1443682362528632913



# On bot shutdown
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    bot_command_channel = client.get_channel(1443682362528632913)
    await bot_command_channel.send('I is ded')







client.run(TOKEN)
