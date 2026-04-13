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


work_cooldowns = {}






#youtube searching
async def get_youtube_video(query):
    youtube = build('youtube', 'v3', developerKey = YOUTUBE_API_KEY)
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=100
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
c.execute('CREATE TABLE IF NOT EXISTS items (item_id INTEGER PRIMARY KEY, name TEXT, price INTEGER, description TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS inventory (user_id TEXT, item_id INTEGER, quantity INTEGER)')
c.execute("INSERT OR IGNORE INTO items VALUES (1, 'lockpick', 50, 'Attempt to steal money from someone')")
c.execute("INSERT OR IGNORE INTO items VALUES (2, 'lock', 75, 'Protects you from being stolen from')")
try:
    c.execute('ALTER TABLE users ADD COLUMN active_locks INTEGER DEFAULT 0')
except:
    pass

conn.commit()



c.execute("DELETE FROM users WHERE user_id LIKE '<Message%'")
conn.commit()



# get quantity of a specific item a user owns
def get_item_quantity(user_id, item_id):
    c.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?', (str(user_id), item_id))
    result = c.fetchone()
    if result is None:
        return 0
    return result[0]

# add item to user inventory
def add_item(user_id, item_id, quantity=1):
    existing = get_item_quantity(user_id, item_id)
    if existing == 0:
        c.execute('INSERT INTO inventory VALUES (?, ?, ?)', (str(user_id), item_id, quantity))
    else:
        c.execute('UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?', (existing + quantity, str(user_id), item_id))
    conn.commit()

# remove item from user inventory
def remove_item(user_id, item_id, quantity=1):
    existing = get_item_quantity(user_id, item_id)
    if existing <= quantity:
        c.execute('DELETE FROM inventory WHERE user_id = ? AND item_id = ?', (str(user_id), item_id))
    else:
        c.execute('UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?', (existing - quantity, str(user_id), item_id))
    conn.commit()

def loose(user, bet):
    update_balance(user, get_balance(user) - bet)

def win(user, bet):
    update_balance(user, get_balance(user) + bet)


async def RPS(message, bet=None):
    def check(m):
        return m.author == message.author and m.channel == message.channel
    user = message.author.id
    #if bet is none, get it from the user
    if bet is None:
        await message.channel.send('How much do you want to bet?')
        response = await client.wait_for('message', check=check)
        bet = int(response.content)

    #balance checks 
    if(bet < 0):
        await message.channel.send('You lil slyyy bitch, you think your better than everyone else? trying to cheat the system? cant belive you. Dumbass')
        return


    balance = get_balance(message.author.id)
    if bet > balance:
        await message.channel.send('You don\'t have enough money!')
        return

    await message.channel.send('rock paper or scissors?')
    response = await client.wait_for('message', check=check)
    rps = str(response.content)

    botarray = ['rock', 'paper', 'scissors']
    botanswer = random.choice(botarray)


    await message.channel.send(f'I picked {botanswer}')

    if rps.lower().startswith('rock'):
        if botanswer == 'rock':
            await message.channel.send('We drew.. your lucky')
            return
        elif botanswer == 'paper':
            await message.channel.send('HA FUCK YOU I WIN, PAPER COVERS ROCK SO HARD')
            loose(user, bet)
        else:
            await message.channel.send('fuck. i lost. just this one time.. rock crushes scissors')
            win(user, bet)
    
    elif rps.lower().startswith('paper'):
        if botanswer == 'rock':
            await message.channel.send('fuck. i lost. just this one time.. paper covers rock')
            win(user,bet)
            return
        elif botanswer == 'paper':
            await message.channel.send('We drew.. your lucky')
        else:
            await message.channel.send('HA FUCK YOU I WIN, SCISSORS CUTS TF OUTA PAPER')
            loose(user, bet)

    elif rps.lower().startswith('scissors'):
        if botanswer == 'rock':
            await message.channel.send('HA FUCK YOU I WIN, ROCK CRUSHES YOUR SCISSORS JUST LIKE I CRUSHED YOUR MOM IN BED')
            loose(user,bet)
            return
        elif botanswer == 'paper':
            await message.channel.send('fuck. i lost. just this one time.. scissors cut paper...')
            win(user, bet)
        else:
            await message.channel.send('We drew.. your lucky')
            return
    else:
        await message.channel.send('thats not a valid option dumbass')





    #win loss for rock paper scissors



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
                loose(message.author.id,bet)
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
                win(message.author.id,bet)
            elif playertotal > dealertotal:
                await message.channel.send('fuck. you win.')
                win(message.author.id,bet)
            elif playertotal < dealertotal:
                await message.channel.send('FUCK YEAEAAAAAA SUCK IT BIOTCHCH I WON.')
                loose(message.author.id,bet)
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
        
        
        
        #help pages
        case s if s.startswith('!help'):
            parts = message.content.split()
            
            if len(parts) == 1:
                # general help page
                await message.channel.send("""Available commands: 
        !help, !hello, !joke, !letslarp, !quote, !8ball, !uwu, !mommyasmr, !daddyasmr, !roll, !guessroll, !rps, !blackjack, !balance, !beg, !donate, !invest, !getinvested, !sellinvested, !leaderboard, !work, @me (PinkGamer), penis, die, expensive, mcdonald, 6, goodnight, !shop, !buy, !inventory, !use
                                            
        Type !help <command> for more info on a specific command""")
            
            else:
                # specific command help
                match parts[1].lower():
                    case 'blackjack' | 'jackblack':
                        await message.channel.send("""**!blackjack** - Play a game of blackjack against me
        Usage: !blackjack <bet> or just !blackjack and I'll ask you
        Commands during game: hit, stand""")
                    case 'rps':
                        await message.channel.send("""**!rps** - Play rock paper scissors against me
        Usage: !rps <bet> or just !rps and I'll ask you""")
                    case 'invest':
                        await message.channel.send("""**!invest** - Invest your money for 5% \returns every 6 hours
        Usage: !invest <amount> or just !invest and I'll ask you
        Related: !getinvested, !sellinvested""")
                    case 'work':
                        await message.channel.send("""**!work** - Makes you solve easy math questions for a little bit of mula. There will be penalties for stupidity!""")
                    case 'donate':
                        await message.channel.send("""**!donate** - Give money to someone else
        Usage: !donate then I'll ask who and how much""")
                    case 'beg':
                        await message.channel.send("""**!beg** - Beg me for money. Maybe I'll give you some. Maybe not.""")
                    
                    case 'quote':
                        await message.channel.send("""**!quote** - Will say a quote from quotes-made-by-ash""")
                    
                    case 'hello':
                        await message.channel.send("""**!hello** - Says hello!""")
                    
                    case 'joke':
                        await message.channel.send("""**!joke** - Tells a dad joke""")
                    
                    case '!letslarp':
                        await message.channel.send("**!letslarp** - idfk, it was bossdro's idea")
                    
                    case '8ball':
                        await message.channel.send("**!8ball** - ask the magic 8 ball any question")

                    case 'uwu': 
                        await message.channel.send("**!uwu** - What do you think it does...")

                    case 'mommyasmr': 
                        await message.channel.send("**!mommyasmr** - grabs a mommy asmr video from youtube")
                    
                    case 'daddyasmr':
                        await message.channel.send("**!daddyasmr** - grabs a daddy asmr video from youtube")

                    case 'roll':
                        await message.channel.send("**!roll** - rolls a d20")

                    case 'guessroll':
                        await message.channel.send("**!guessroll** - try and guess what a d20 will roll")

                    case 'balance':
                        await message.channel.send("""**!balance** - checks your balance
  Related Commands: !invest, !getinvested, !blackjack, !work""")
                        
                    case 'getinvested':
                        await message.channel.send("""**!getinvested** - tells you how much money you have invested
Related Commands: !invest, !sellinvested, !work""")
                        
                    case 'sellinvested':
                        await message.channel.send("""**!sellinvested** - sells an amount of money that you have invested to get it back in your bank account""")

                    case 'leaderboard':
                        await message.channel.send("**!leaderboard** - shows a leaderboard of the top 5 richest people using this bot!")

                    case 'penis':
                        await message.channel.send("**penis** - penis command")

                    case 'die':
                        await message.channel.send("**die** - die command")
                    
                    case 'expensive':
                        await message.channel.send("**expensive** - expensive command")
                    
                    case 'mcdonald':
                        await message.channel.send("**mcdonald** - mcdonald command (im hungry)")
                    
                    case '6':
                        await message.channel.send("**6** - 7")

                    case 'goodnight':
                        await message.channel.send("**goodnight** - tells whoever says goodnight, goodnight back")
                    
                    case 'shop':
                        await message.channel.send("""**!shop** - Shows all items available to buy""")

                    case 'buy':
                        await message.channel.send("""**!buy** - Buy an item from the shop
                    Usage: !buy <item name>""")

                    case 'inventory':
                        await message.channel.send("""**!inventory** - Shows all items you currently own""")

                    case 'use':
                        await message.channel.send("**!use** - Uses an item in inventory. Help pages for items WIP")



                                                                     
                    case _:
                        await message.channel.send(f'no help page for {parts[1]} dummy')        
            
            





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
    
        
        case '!shop':
            # get all items from the shop
            c.execute('SELECT item_id, name, price, description FROM items')
            items = c.fetchall()
            
            shop = '🏪 **Shop** 🏪\n'
            for item_id, name, price, description in items:
                shop += f'**{name}** - ${price}\n{description}\n\n'
            
            await message.channel.send(shop)

        case s if s.startswith('!buy'):
            parts = message.content.split()
            if len(parts) < 2:
                await message.channel.send('Usage: !buy <item name>')
                return
            
            item_name = parts[1].lower()
            
            # check if item exists
            c.execute('SELECT item_id, price FROM items WHERE name = ?', (item_name,))
            result = c.fetchone()
            if result is None:
                await message.channel.send(f'no item called {item_name} dummy')
                return
            
            item_id, price = result
            balance = get_balance(message.author.id)
            
            # check if they can afford it
            if balance < price:
                await message.channel.send(f'you cant afford that, you need ${price} and you only have ${balance}')
                return
            
            # buy the item
            update_balance(message.author.id, balance - price)
            add_item(message.author.id, item_id)
            await message.channel.send(f'you bought a {item_name} for ${price}!')

        case '!inventory':
            # get all items in the user's inventory
            c.execute('''SELECT items.name, inventory.quantity 
                        FROM inventory 
                        JOIN items ON inventory.item_id = items.item_id 
                        WHERE inventory.user_id = ?''', (str(message.author.id),))
            items = c.fetchall()
            
            if len(items) == 0:
                await message.channel.send('your inventory is empty you broke bum')
                return
            
            username = message.author.display_name
            inv = f'🎒 **{username}\'s Inventory** 🎒\n'
            for name, quantity in items:
                inv += f'{name} x{quantity}\n'
            
            await message.channel.send(inv)
        
        
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
        
        case '!uwu':
            
            uwu = ['https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGZ5M2RnZW5zbnpic3B6NHk4aTRpYnIwYzdoNzJmNDV3cGlqcjN6MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/nXy2VIqUP8caHjDheV/giphy.gif',
                   'https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWVwMHh0ZHNpbXRnOXA2ZmMzYXNpbGFoYjljZWhkeTR0Mno1aXo4aiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/AR6goyT6NE9e3CqmqW/giphy.gif',
                   'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExcmhqNDExdnNrdGZkaXkzbnY5cDloOGFyN203NzVqaGJtMmNqYnl6ZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fe8oe4XGRNYpEysGj7/giphy.gif',
                   'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NTFvYTNwemV2a3Fwd3ZldnpyYThqNDJhYWlyM3k5cTBmM29lbjRrOSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/JPcUECC1kA0um34kFw/giphy.gif',
                   'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeGtpOHAzemQxYjBwaHNnZ2prYzA2d2d3MnFjaGkybW53dGkyaDY4ciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/yprzrPVHIK1QNJngve/giphy.gif',
                   'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3bnlyeGpzdGV3cGhhdjVwYzFjMHRob25yMG9qeGR5djY4cG1rdm52YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/jBCsvJ7tWea7QSuFWm/giphy.gif',
                   'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3bnlyeGpzdGV3cGhhdjVwYzFjMHRob25yMG9qeGR5djY4cG1rdm52YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/J509hr2j0oMejwlKOS/giphy.gif',
                   'https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWd4NGYwczV5ZzQxdXhlaWJhaW1idXhjaHZodzFqYmI3bjd6ZTRuOCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/N56wAElDGIJgJ35ijc/giphy.gif',
                   'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3Z3NucmhnM281cXg5dnlxbnJ6aDkwNGw3dzJ0ZncwOXk0c21peGJ6ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/DhbZy2EKyVjJ8zPfY3/giphy.gif',
                   'https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3czU1NThlNHNlZ3ZnbnJ4Ymh4ZWcwZ3JzNnNzczhpMDFkNmJ6Nmp4YyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/ldgC6CU984lmMc2LaG/giphy.gif',
                   'https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZmtzenBmMHRhcGVhYXBlcnc0MXVvbGE0OGV1YzZtcWs5bHNpd2F1dCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/oHxvbzgmkQa4DVwAu1/giphy.gif']
            await message.channel.send(random.choice(uwu))

        case s if s.startswith('!8ball'):
            ball = ['Yes', 'No', 'Maybe', '5 bucks is 5 bucks', 'dont even think about it']
            await message.channel.send(random.choice(ball))


        #rock paper scissors game
        case s if s.startswith('!rps'):
            await message.channel.send('Ohhhhhh a game of rock paper scissors. THE classic ro sham bo')
            parts = message.content.split()
            if len(parts) > 1:
                try:
                    bet = int(parts[1])
                    await RPS(message, bet)
                except ValueError:
                    await message.channel.send('I only accept MONEY as a bet. nothing else')
            else:
                await RPS(message)



        case '!daddyasmr':
                url = await get_youtube_video('daddy asmr')
                await message.channel.send(f'you werido. still listening to that? dont you have a boyfriend to whisper to you instead...? well. here you go i guess. {url}')

            
        case '!leaderboard':
            c.execute('SELECT user_id, balance, invested FROM users ORDER BY (balance + invested) DESC LIMIT 5')
            results = c.fetchall()
            
            if len(results) == 0:
                await message.channel.send('No one has any money! (somethings probably wrong)')
                return
            
            leaderboard = '🏆 **Leaderboard** 🏆\n'
            for i, (user_id, balance, invested) in enumerate(results, 1):
                total = int(balance + invested)
                user = client.get_user(int(user_id))
                username = user.display_name if user else 'Unknown'
                leaderboard += f'{i}. {username} - ${total}\n'

            await message.channel.send(leaderboard)        
        
        case '!work':
            user_id = message.author.id
            
            # check cooldown
            if user_id in work_cooldowns:
                time_left = 60 - (asyncio.get_event_loop().time() - work_cooldowns[user_id])
                if time_left > 0:
                    await message.channel.send(f'you\'re on cooldown dummy, wait {int(time_left)} more seconds')
                    return

            def check(m):
                return m.author == message.author and m.channel == message.channel
            
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            operator = random.choice(['+', '-', '*'])
            
            if operator == '+':
                answer = a + b
            elif operator == '-':
                answer = a - b
            else:
                answer = a * b
            
            await message.channel.send(f'You want money? EARN IT. Whats {a} {operator} {b}?')
            
            try:
                response = await asyncio.wait_for(client.wait_for('message', check=check), timeout=10)
                guess = int(response.content)
            except asyncio.TimeoutError:
                work_cooldowns[user_id] = asyncio.get_event_loop().time()
                await message.channel.send('too slow dummy, no money for you. 1 min cooldown!')
                return
            except ValueError:
                await message.channel.send('thats not a number dummy')
                return
            
            if guess == answer:
                reward = random.randint(5, 50)
                update_balance(message.author.id, get_balance(message.author.id) + reward)
                await message.channel.send(f'correct! here\'s ${reward} you earned it')
            else:
                work_cooldowns[user_id] = asyncio.get_event_loop().time()
                await message.channel.send(f'WRONG. the answer was {answer}. 1 min cooldown!')                
        
        case 'six':
            await message.channel.send('seven')
        
        
        case s if s.startswith('!use'):
            parts = message.content.split()
            user_id = message.author.id
            
            if len(parts) < 2:
                await message.channel.send('Usage: !use <item>')
                return
            
            item_name = parts[1].lower()
            
            match item_name:
                case 'lock':
                    # check if they have a lock
                    if get_item_quantity(user_id, 2) == 0:
                        await message.channel.send('you dont have any locks dummy')
                        return
                    
                    # check if they already have 2 active locks
                    c.execute('SELECT active_locks FROM users WHERE user_id = ?', (str(user_id),))
                    result = c.fetchone()
                    active = result[0] if result else 0
                    
                    if active >= 2:
                        await message.channel.send('you already have 2 locks active, thats the max!')
                        return
                    
                    # activate the lock
                    remove_item(user_id, 2)
                    c.execute('UPDATE users SET active_locks = ? WHERE user_id = ?', (active + 1, str(user_id)))
                    conn.commit()
                    await message.channel.send(f'lock activated! you now have {active + 1} active lock(s)')
                
                case 'lockpick':
                    # check if they have a lockpick
                    if get_item_quantity(user_id, 1) == 0:
                        await message.channel.send('you dont have any lockpicks dummy')
                        return
                    
                    def check(m):
                        return m.author == message.author and m.channel == message.channel

                    # get target from ping, username, or prompt
                    if len(message.mentions) > 0:
                        target_id = message.mentions[0].id
                    elif len(parts) > 2:
                        # try to find by username
                        username_search = parts[2].lower()
                        target = discord.utils.find(lambda m: m.name.lower() == username_search or m.display_name.lower() == username_search, message.guild.members)
                        if target is None:
                            await message.channel.send(f'cant find anyone called {parts[2]}')
                            return
                        target_id = target.id
                    else:
                        await message.channel.send('who do you want to steal from? (@ them or type their username)')
                        response = await client.wait_for('message', check=check)
                        if len(response.mentions) > 0:
                            target_id = response.mentions[0].id
                        else:
                            username_search = response.content.lower()
                            target = discord.utils.find(lambda m: m.name.lower() == username_search or m.display_name.lower() == username_search, message.guild.members)
                            if target is None:
                                await message.channel.send(f'cant find anyone called {response.content}')
                                return
                            target_id = target.id
                    
                    if target_id == user_id:
                        await message.channel.send('you cant steal from yourself dummy')
                        return
                    
                    # check if target has active locks
                    c.execute('SELECT active_locks FROM users WHERE user_id = ?', (str(target_id),))
                    result = c.fetchone()
                    target_locks = result[0] if result else 0
                    
                    if target_locks > 0:
                        # consume one lock and break the lockpick
                        c.execute('UPDATE users SET active_locks = ? WHERE user_id = ?', (target_locks - 1, str(target_id)))
                        conn.commit()
                        remove_item(user_id, 1)
                        await message.channel.send(f'they had a lock! your lockpick broke and their lock was used up. <@{target_id}> is safe... this time')
                        return
                    
                    # steal a random % of their balance
                    target_balance = get_balance(target_id)
                    if target_balance == 0:
                        await message.channel.send('they\'re broke, nothing to steal!')
                        return

                    #LINE 1000!!!!!!!!!!!!! WOOOOOOOOOOO
                    steal_percent = random.randint(10, 30)
                    stolen = int(target_balance * (steal_percent / 100))
                    
                    remove_item(user_id, 1)
                    update_balance(target_id, target_balance - stolen)
                    update_balance(user_id, get_balance(user_id) + stolen)
                    await message.channel.send(f'you stole ${stolen} ({steal_percent}%) from <@{target_id}>! 😈')

                case _:
                    await message.channel.send(f'no item called {item_name}')

        case _:
            pass
        
    

    #if the word is contained within the message

    if 'expensive' in message.content.lower():
        await message.channel.send('kidna espesive')

    if 'mcdonald' in message.content.lower():
        await message.channel.send('mcdondalds')

    if f'<@{botId}>' in message.content:
        await message.channel.send('You rang?')
    
    if 'goodnight' in message.content.lower():
        username = message.author.display_name
        await message.channel.send(f'goodnight {username}')




client.run(TOKEN)