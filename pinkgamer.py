import sqlite3
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








#database setup for bank system, will add more later
conn = sqlite3.connect('bank.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT, balance INTEGER)')
conn.commit()



def get_balance(user_id):
    c.execute('SELECT balance FROM users WHERE user_id = ?', (str(user_id),))
    result = c.fetchone()
    if result is None:
        c.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (str(user_id), 100))
        conn.commit()
        return 100
    return result[0]

def update_balance(user_id, amount):
    c.execute('UPDATE users SET balance = ? WHERE user_id = ?', (amount, str(user_id)))
    conn.commit()


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
    await message.channel.send('How much do you want to bet?')
    
    def check(m):
        return m.author == message.author and m.channel == message.channel
    
    response = await client.wait_for('message', check=check)
    bet = int(response.content)
    if(bet < 0):
        await message.channel.send('You lil slyyy bitch, you think your better than everyone else? trying to cheat the system? cant belive you. Dumbass')
        return
    

    balance = get_balance(message.author.id)
    if bet > balance:
        await message.channel.send('You don\'t have enough money!')
        return
    
    
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [f'{rank}{suit}' for rank in ranks for suit in suits]
    random.shuffle(deck)

    

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
                update_balance(message.author.id, balance + bet)
            elif playertotal > dealertotal:
                await message.channel.send('fuck. you win.')
                update_balance(message.author.id, balance + bet)
            elif playertotal < dealertotal:
                await message.channel.send('FUCK YEAEAAAAAA SUCK IT BIOTCHCH I WON.')
                update_balance(message.author.id, balance - bet)
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
        await message.channel.send("""Available commands: !hello, !roll, !help, penis, expensive, mcdonald, !blackjack, !guessroll, die
pinging the bot, !joke, !balance, !letslarp, !quote, !beg""")



    #hello command
    if message.content == '!hello':
        helloMsg = ['Hey there!', 'Hello!', 'Hi there!', 'Hiya', 'BANANA', 'sup', 'I have no idea what is going on', 'Hi Earthling']
        await message.channel.send(random.choice(helloMsg))



    #revisit later to make cooler rolling system
    if message.content == '!roll':
        await message.channel.send(f'🎲 You rolled a {roll()} from a d20!')
    
    #penis line
    if message.content == 'penis':
        await message.channel.send('show it to me *NOW*')
    


    # greysons ideas
    if 'expensive' in message.content.lower(): 
        await message.channel.send('kidna espesive')


    
    if 'mcdonald' in message.content.lower():
        await message.channel.send('mcdondalds')



    if message.content == '!blackjack' or message.content == '!jackblack':
        await message.channel.send('Ohhhhhh a game of blackjack you wanna play I see, alright. Im gonna destroy you!')
        await blackjack(message)



    if message.content == '!guessroll':
        rolled = roll()
        await message.channel.send('whatcha guess?')
        response = await client.wait_for('message', check=check)
        if response == rolled:
            await message.channel.send(f'holy fucking shit your a wizard <@{message.author.id}>')
        else:
            await message.channel.send(f'OMG YOUR SO SMART <@{message.author.id}>')
            time.sleep(5)
            await message.channel.send(f'nvm fuckin dumbass, you really thought you got that? EVERYONE CLOWN ON <@{message.author.id}> FOR BEINGS SO STUPID')
            await message.channel.send(f'the roll was {rolled} dumbass')



    if 'die' in message.content.lower():
        await message.channel.send(f'KYS')

    #self ping response
    if '<@1492354981033017444>' in message.content:
        await message.channel.send('You rang?')



    #i set up a whole database with user balances
    if message.content == '!balance':
        balance = get_balance(message.author.id)
        await message.channel.send(f'<@{message.author.id}> you have ${balance}')



    #dad joke
    if message.content == '!joke':
        await message.channel.send('Dad')

    #bossdrobots idea. No clue what it means
    if message.content == '!letslarp':
        await message.channel.send('just this one e')

    if message.content == '!beg':
        await message.channel.send(f'You would wouldnt you, lil bitch. fucking poor. imaging needing to beg from ME. Ill petty you this one time')
        update_balance(message.author.id, get_balance(message.author.id) + 1)  # Add $1 to the user's balance


    #pulls from my qoutes channel
    if message.content == '!quote':
        quotes_channel = client.get_channel(1435661484712657008)
        messages = []
        async for msg in quotes_channel.history(limit=5000):
            messages.append(msg)
        quote = random.choice(messages)
        await message.channel.send(f'"{quote.content}" - {quote.author.display_name}')


client.run(TOKEN)