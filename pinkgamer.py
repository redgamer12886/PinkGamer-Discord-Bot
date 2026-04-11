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
    bot_command_channel = client.get_channel(1443682362528632913)
    await bot_command_channel.send('I am ready! (bots on <@585178815253446685>)')

@client.event
async def on_message(message):

    #all the text commands for all the stuff sit does

    if message.author == client.user:
        return



    #make sure i update every time i add something
    if message.content == '!help':
        await message.channel.send("""Available commands: !hello, !roll, !help, penis, expensive, mcdonald""")



    #hello command
    if message.content == '!hello':
        await message.channel.send('Hey there!')



    #revisit later to make cooler rolling system
    if message.content == '!roll':
        import random
        result = random.randint(1, 20)
        await message.channel.send(f'🎲 You rolled a {result}!')
    
    #penis line
    if message.content == 'penis':
        await message.channel.send('show it to me *NOW*')
    

    # greysons ideas
    if 'expensive' in message.content.lower(): 
        await message.channel.send('kidna espesive')


    
    if 'mcdonald' in message.content.lower():
        await message.channel.send('mcdondalds')



client.run(TOKEN)
