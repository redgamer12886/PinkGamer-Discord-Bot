import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '!help':
        await message.channel.send('Available commands: !hello, !roll, !help, penis')

    if message.content == '!hello':
        await message.channel.send('Hey there!')

    if message.content == '!roll':
        import random
        result = random.randint(1, 20)
        await message.channel.send(f'🎲 You rolled a {result}!')

    if message.content == 'penis':
        await message.channel.send('show it to me *NOW*')

client.run(TOKEN)
