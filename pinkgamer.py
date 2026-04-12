import sqlite3
import random
import discord
import os
import random
import time
import asyncio

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
    aces = 0
    await message.channel.send(f'Drew: {card}')
    if card.startswith(('J', 'Q', 'K')):
        value = 10
        
        #checks for ace or jack, or queen, or king, and assigns the value accordingly. will do extra ace logic later
    elif card.startswith('A'):
        value = 11
        aces += 1
    else:
        value = int(card[:-1])

    return value, aces

#blackjack function
async def blackjack(message, bet=None):

    def check(m):
        return m.author == message.author and m.channel == message.channel
    
    #if bet is none, get it from the user
    if bet is None:
        await message.channel.send('How much do you want to bet?')
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
    aces = 0
    # deal 2 cards to start
    value, ace = await draw_card(message, deck)
    cards.append(value)
    aces += ace
    value, ace = await draw_card(message, deck)
    cards.append(value)
    aces += ace

    # player's turn loop
    while True:
        await message.channel.send(f'Your total is {sum(cards)}. Hit or stand?')
        response = await client.wait_for('message', check=check)

        if response.content.lower() == 'hit':
            value, ace = await draw_card(message, deck)
            cards.append(value)
            aces += ace
            if sum(cards) > 21 and aces == 0:
                await message.channel.send('You busted OWO! *I wins*.')
                update_balance(message.author.id, balance - bet)
                return  # end the game
            #if ace in your hand. then it changes it to a 1 if you would have busted
            elif sum(cards) > 21 and aces > 0:
                cards[cards.index(11)] = 1
                aces -= 1


        elif response.content.lower() == 'stand':
            await message.channel.send('You chose to stand. MY TURN!')
            dealeraces = 0
            dealercards = []
            value, ace = await draw_card(message, deck)
            dealercards.append(value)
            dealeraces += ace

            while sum(dealercards) < 17:
                value, ace = await draw_card(message, deck)
                dealercards.append(value)
                dealeraces += ace
                #ace logic for dealer
                while sum(dealercards) > 21 and dealeraces > 0:
                    dealercards[dealercards.index(11)] = 1
                    dealeraces -= 1
            
            
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

    if message.author == client.user: 
        return

    #all the text commands for all the stuff sit does

    def check(m):
        return m.author == message.author and m.channel == message.channel


    #for all commands that are exactly that message
    match message.content.lower():
        case '!help':
            #make sure i update every time i add something
            await message.channel.send("""Available commands: !hello, !roll, !help, penis, expensive, mcdonald, !blackjack, !guessroll, die, pinging the bot, !joke, !balance, !letslarp, !quote, !beg, !donate""")
        case '!hello':
            #hello stuff
            helloMsg = ['Hey there!', 'Hello!', 'Hi there!', 'Hiya', 'BANANA', 'sup', 'I have no idea what is going on', 'Hi Earthling']
            await message.channel.send(random.choice(helloMsg))
        case '!roll':
            #rolls a d20
            await message.channel.send(f'🎲 You rolled a {roll()} from a d20!')
        case 'penis':
            #penis line
            await message.channel.send('show it to me *NOW*')
    
        case s if s.startswith('!blackjack') or s.startswith('!jackblack'):
            await message.channel.send('Ohhhhhh a game of blackjack you wanna play I see, alright. Im gonna destroy you!')
            parts = message.content.split()
            if len(parts) > 1:
                try:
                    bet = int(parts[1])
                    await blackjack(message, bet)
                except ValueError:
                    await message.channel.send('I only accept MONEY as a bet. nothing else')
            else:
                await blackjack(message)
            

        case s if s.startswith('!guessroll'):
            rolled = roll()

            parts = message.content.split()
            if len(parts) > 1:
                try:
                    response = int(parts[1])
                except ValueError:
                    await message.channel.send('I dont have a die that can roll that')
            else:
                await message.channel.send('whatcha guess?')
                response = await client.wait_for('message', check=check)
                response = int(response.content)
            
            
            if response == rolled:
                await message.channel.send(f'holy fucking shit your a wizard <@{message.author.id}>')
            else:
                await message.channel.send(f'OMG YOUR SO SMART <@{message.author.id}>')
                await asyncio.sleep(5)
                await message.channel.send(f'nvm fuckin dumbass, you really thought you got that? EVERYONE CLOWN ON <@{message.author.id}> FOR BEINGS SO STUPID')
                await message.channel.send(f'the roll was {rolled} dumbass')
        
        case 'die':
            await message.channel.send(f'KYS')

        case '<@1492354981033017444>':
            #self ping response
            await message.channel.send('You rang?')

        case '!balance':
            #checks a users balance
            balance = get_balance(message.author.id)
            await message.channel.send(f'<@{message.author.id}> you have ${balance}')

        case '!joke':
            #dad joke
            await message.channel.send('Dad')
        
        case '!letslarp':
            #bossdrobots idea. No clue what it means
            await message.channel.send('just this one e')

        case '!beg':
            begamount = [1, 1, 1, 5, 10, 5, 2, 3, 1, 1, 1, 1, 10, 3, 4, 5, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 10]
            choice = random.choice(begamount)
            await message.channel.send(f'You would wouldnt you, lil bitch. fucking poor. imaging needing to beg from ME. Ill pitty you this one time. Heres ${choice}')

            update_balance(message.author.id, get_balance(message.author.id) + choice )  # Add $1 to the user's balance
        
        case '!quote':
            #pulls from my qoutes channel
            quotes_channel = client.get_channel(1435661484712657008)
            messages = []
            async for msg in quotes_channel.history(limit=5000):
                messages.append(msg)
            quote = random.choice(messages)
            await message.channel.send(f'{quote.content}')

        case '!donate':
            #donate money to someone else
            startuser = message.author.id

            await message.channel.send(f'OH BOYYY LOOK AT MR MONEY BAGS HERE, your so sweet on giving money to someone, who would you like to give money too? (@ them)')
            
            response = await client.wait_for('message', check=check)
            if len(response.mentions) == 0:
                await message.channel.send('You need to @ someone!')
                return
            else:
                pooruser = response.mentions[0].id

            await message.channel.send('How much would you like to give deary?')
            response = await client.wait_for('message', check=check)

            try:
                amount = int(response.content)
            except ValueError:
                await message.channel.send('That\'s not a number dummy!')
                return
            #checking for neg amounts
            if amount < 0:
                await message.channel.send(f'tsk tsk, trying to rob someone i see. maybe a future command.... <@{pooruser}> <@{startuser}> IS TRYING TO ROB YOU. RUNN FOR YOUR FUCKING LIFE')
                return
            userbal = get_balance(startuser)
            if userbal < amount:
                await message.channel.send(f'I know <@{pooruser}> is broke, but dont break yourself helping them!')
            else:
                update_balance(pooruser, get_balance(pooruser) + amount)
                update_balance(startuser, get_balance(startuser) - amount)
                await message.channel.send(f'Good job <@{startuser}> your such a good person for helping out <@{pooruser}> and giving them ${amount}!')
        case _:
            pass
        

    
    #if the word is contained within the message

    if 'expensive' in message.content.lower():
        await message.channel.send('kidna espesive')

    if 'mcdonald' in message.content.lower():
        await message.channel.send('mcdondalds')

    




client.run(TOKEN)