import sqlite3
import random
import discord
import os
import time
import asyncio


from discord.ext import tasks
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
botId = '1492354981033017444'



intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)







#youtube searching
async def get_youtube_video(query):
    youtube = build('youtube', 'v3', developerKey = YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=20
    )
    response = request.execute()
    videos = response['items']
    video = random.choice(videos)
    video_id = video['id']['videoId']
    return f'https://www.youtube.com/watch?v={video_id}'



#database setup for bank system, will add more later
conn = sqlite3.connect('bank.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT, balance INTEGER, invested FLOAT DEFAULT 0)')
conn.commit()


#invest helper functions

#gets invested amount
def get_invested(user_id):
    c.execute('SELECT invested FROM users WHERE user_id = ?', (str(user_id),))
    result = c.fetchone()

    if result is None:
        return 0
    return result[0]

#update invested
def update_invested(user_id, amount):
    c.execute('UPDATE users SET invested = ? WHERE user_id = ?', (int(amount), str(user_id)))
    conn.commit()







#bank account helper functions
#get bal for the moeny stuff
def get_balance(user_id):
    c.execute('SELECT balance FROM users WHERE user_id = ?', (str(user_id),))
    result = c.fetchone()
    if result is None:
        c.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (str(user_id), 100))
        conn.commit()
        return 100
    return result[0]

#update bal for moeny stuff
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
        if sum(cards) == 21:
                await message.channel.send('HOLY FUCKING SHIT MON, YOU DID BLACKED YOUR JACK. bowser would be proud')
                update_balance(message.author.id, balance + (bet * 1.5))
                return
        
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




@tasks.loop(hours=6)
async def apply_interest():
    bot_command_channel = client.get_channel(1443682362528632913)
    c.execute('SELECT user_id, invested FROM users WHERE invested > 0')
    users = c.fetchall()
    for user_id, invested in users:
        update_invested(user_id, (invested * 1.05))
    await bot_command_channel.send('INVESTMENTS ARE PROFITABLE')


    

#on bot startup
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    bot_command_channel = client.get_channel(1443682362528632913)
    await bot_command_channel.send('I am ready! (bots on <@585178815253446685>)')
    apply_interest.start()
    
#on message is sent
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
            await message.channel.send("""Available commands: !hello, !roll, !help, penis, expensive, mcdonald, !blackjack, !guessroll, die, pinging the bot, !joke, !balance, !letslarp, !quote, !beg, !donate, !mommyasmr, 6, !invest, !getinvested, !sellinvested""")
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
        
        #i dont even know anymore... pulss a youtube video. and now i can search yt. pretty neat
        case '!mommyasmr':
            url = await get_youtube_video('mommy asmr')
            await message.channel.send(f'you werido. still listening to that? dont you have a girlfriend to whisper to you instead...? well. here you go i guess. {url}')
        
        case '6':
            await message.channel.send(f'7')

        case s if s.startswith('!invest'):
            user = message.author.id
            parts = message.content.split()
            username = message.author.display_name
            
            if len(parts) > 1:
                try:
                    amount = int(parts[1])
                except ValueError:
                    await message.channel.send('you gotta invest money, not whatever that is')
                    return
                    
                if amount <= 0:
                    await message.channel.send('you cant invest negative numbers dummy')
                    return
                
                balance = get_balance(user)
                if amount > balance:
                    await message.channel.send('You don\'t have enough money!')
                    return

                update_invested(user, get_invested(user) + amount)
                update_balance(user, balance - amount)
                await message.channel.send(f'Looks like someones being smart with their money. {username} invested ${amount}')
            else: 
                await message.channel.send('How much would you like to invest?')
                response = await client.wait_for('message', check=check)

                try:
                    amount = int(response.content)
                except ValueError:
                    await message.channel.send('you gotta invest money, not whatever that is')
                    return

                if amount <= 0:
                    await message.channel.send('you cant invest negative numbers dummy')
                    return

                balance = get_balance(user)
                if amount > balance:
                    await message.channel.send('You don\'t have enough money!')
                    return

                update_invested(user, get_invested(user) + amount)
                update_balance(user, balance - amount)
                await message.channel.send(f'Looks like someones being smart with their money. {username} invested ${amount}')

        case s if s.startswith('!sellinvested'):
            user = message.author.id
            parts = message.content.split()
            username = message.author.display_name

            if len(parts) > 1:
                try:
                    amount = int(parts[1])
                except ValueError:
                    await message.channel.send('you gotta sell money, not whatever that is')
                    return

                if amount <= 0:
                    await message.channel.send('you cant sell negative numbers dummy')
                    return

                invest = get_invested(user)
                if amount > invest:
                    await message.channel.send('You don\'t have enough invested!')
                    return

                balance = get_balance(user)
                update_invested(user, invest - amount)
                update_balance(user, balance + amount)
                await message.channel.send(f'Looks like someones wants their money. {username} sold ${amount}')

            else:
                await message.channel.send('How much would you like to sell?')
                response = await client.wait_for('message', check=check)

                try:
                    amount = int(response.content)
                except ValueError:
                    await message.channel.send('you gotta sell money, not whatever that is')
                    return

                if amount <= 0:
                    await message.channel.send('you cant sell negative numbers dummy')
                    return

                invest = get_invested(user)
                if amount > invest:
                    await message.channel.send('You don\'t have enough invested!')
                    return

                balance = get_balance(user)
                update_invested(user, invest - amount)
                update_balance(user, balance + amount)
                await message.channel.send(f'Looks like someones wants their money. {username} sold ${amount}')



        case '!getinvested':
            user_id = message.author.id
            username = message.author.display_name
            amount = get_invested(user_id)
            await message.channel.send(f'Ooo looky, {username} has ${amount} invested. Pretty hot')

        #super user commands
        case s if s.startswith('!fixuser'):
            print(f'author id: {message.author.id}')
            print(f'mentions: {message.mentions}')
            if message.author.id == 585178815253446685:
                if len(message.mentions) == 0:
                    await message.channel.send('You need to @ someone!')
                    return
                target_id = message.mentions[0].id
                c.execute('UPDATE users SET balance = 100, invested = 0 WHERE user_id = ?', (str(target_id),))
                conn.commit()
                await message.channel.send(f'Fixed <@{target_id}>')
            else:
                await message.channel.send('You don\'t have permission to do that!')        
        
        case _:
            pass
        

    
    #if the word is contained within the message

    if 'expensive' in message.content.lower():
        await message.channel.send('kidna espesive')

    if 'mcdonald' in message.content.lower():
        await message.channel.send('mcdondalds')

    if f'<@{botId}>' in message.content:
        await message.channel.send('You rang?')
    




client.run(TOKEN)