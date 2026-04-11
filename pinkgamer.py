
import random
import discord
import os
import random
import time

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


#strickty for use in blackjack function
async def draw_card(message, deck):
    card = deck.pop()
    await message.channel.send(f'Drew: {card}')
    if card.startswith(('J', 'Q', 'K')):
        value = 10
        
        #checks for ace or jack, or queen, or king, and assigns the value accordingly. will do extra ace logic later
    elif card.startswith('A'):
        value = 11
    else:
        value = int(card[:-1])

    return value

#blackjack function
async def blackjack(message):
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [f'{rank}{suit}' for rank in ranks for suit in suits]
    random.shuffle(deck)

    def check(m):
        return m.author == message.author and m.content.lower() in ['hit', 'stand']

    cards = []

    # deal 2 cards to start
    cards.append(await draw_card(message, deck))
    cards.append(await draw_card(message, deck))

    # player's turn loop
    while True:
        await message.channel.send(f'Your total is {sum(cards)}. Hit or stand?')
        response = await client.wait_for('message', check=check)

        if response.content.lower() == 'hit':
            cards.append(await draw_card(message, deck))
            if sum(cards) > 21:
                await message.channel.send('You busted OWO! *I wins*.')
                return  # end the game

        elif response.content.lower() == 'stand':
            await message.channel.send('You chose to stand. MY TURN!')
            dealercards = []
            dealercards.append(await draw_card(message, deck))

            while sum(dealercards) < 17:
                dealercards.append(await draw_card(message, deck))

            playertotal = sum(cards)
            dealertotal = sum(dealercards)

            if dealertotal > 21:
                await message.channel.send('I busted OWO! *You wins*.')
            elif playertotal > dealertotal:
                await message.channel.send('fuck. you win.')
            elif playertotal < dealertotal:
                await message.channel.send('FUCK YEAEAAAAAA SUCK IT BIOTCHCH I WON.')
            else:
                await message.channel.send('its a tie...')
            return  # end the game


def roll():
    result = random.randint(1, 20)
    return result



@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    bot_command_channel = client.get_channel(1443682362528632913)
    await bot_command_channel.send('I am ready! (bots on <@585178815253446685>)')

@client.event
async def on_message(message):

    #all the text commands for all the stuff sit does

    def check(m):
        return m.author == message.author and m.channel == message.channel




    if message.author == client.user:
        return



    #make sure i update every time i add something
    if message.content == '!help':
        await message.channel.send("""Available commands: !hello, !roll, !help, penis, expensive, mcdonald, !blackjack, !guessroll""")



    #hello command
    if message.content == '!hello':
        await message.channel.send('Hey there!')



    #revisit later to make cooler rolling system
    if message.content == '!roll':
        await message.channel.send(f'🎲 You rolled a {roll()}!')
    
    #penis line
    if message.content == 'penis':
        await message.channel.send('show it to me *NOW*')
    

    # greysons ideas
    if 'expensive' in message.content.lower(): 
        await message.channel.send('kidna espesive')


    
    if 'mcdonald' in message.content.lower():
        await message.channel.send('mcdondalds')


    if message.content == '!blackjack':
        await message.channel.send('Ohhhhhh a game of blackjack you wanna play I see, alright. Im gonna destroy you!')
        await blackjack(message)



    if message.content == '!guessroll':
        rolled = roll()
        await message.channel.send('whatcha guess?')
        response = await client.wait_for('message', check=check)
        if response == roll:
            await message.channel.send(f'holy fucking shit your a wizard <@{message.author.id}>')
        else:
            await message.channel.send(f'OMG YOUR SO SMART <@{message.author.id}>')
            time.sleep(5)
            await message.channel.send(f'nvm fuckin dumbass, you really thought you got that? <@743189642836443260> CLOWN ON <@{message.author.id}> FOR BEINGS SO STUPID')
            await message.channel.send(f'the roll was {rolled} dumbass')


client.run(TOKEN)
