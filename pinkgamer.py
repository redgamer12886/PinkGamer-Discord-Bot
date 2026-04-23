import sqlite3
import random
import discord
import os
import time
import asyncio

# importing from other files ive writen for better organization. 
# gamefunctions is for functions related to games
# databasefunctions is for functions related to the database. will add more as i go along
from database import update_balance, get_balance, get_invested, update_invested, add_item, get_item_quantity, remove_item

from gamefunctions import RPS, blackjack, roll
from database import c, conn, setup_database
from help_commands import help_command
from items import buy, inventory, shop, use

from superusercommands import superuser_commands


# sets up the database, creates tables if they dont exist, and adds default items to the shop. also removes any users that are actually messages (from when i fucked up and put a message object in there instead of a user id)
setup_database()
#hah


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



@tasks.loop(hours=6)
async def apply_interest():

    bot_command_channel = client.get_channel(1443682362528632913)
    c.execute('SELECT user_id, invested FROM users WHERE invested > 0')
    users = c.fetchall()
    for user_id, invested in users:
        update_invested(user_id, (invested * 1.05))
    await bot_command_channel.send('INVESTMENTS ARE PROFITABLE')






# On bot startup
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    bot_command_channel = client.get_channel(1443682362528632913)
    await bot_command_channel.send('I am ready! (bots on <@585178815253446685>)')
    apply_interest.start()

#on message is sent
@client.event
async def on_message(message):
    # ignores messages from the bot itself
    if message.author == client.user: 
        return

    # All the text commands for all the stuff it does

    def check(m):
        
        return m.author == message.author and m.channel == message.channel


    # for all commands that are exactly that message
    match message.content.lower():
        
        # Help pages
        case s if s.startswith('!help'):
            await message.channel.send('helping')
            await help_command(message)


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
            await shop(message, client)

        case s if s.startswith('!buy'):
           await buy(message, client) 

        case '!inventory':
            # get all items in the user's inventory
            await inventory(message, client)
        
        


        case s if s.startswith('!blackjack') or s.startswith('!jackblack'):
            await message.channel.send('Ohhhhhh a game of blackjack you wanna play I see, alright. Im gonna destroy you!')
            parts = message.content.split()
            if len(parts) > 1:
                try:
                    bet = int(parts[1])
                    await blackjack(message, client, bet)
                except ValueError:
                    await message.channel.send('I only accept MONEY as a bet. nothing else')
            else:
                await blackjack(message, client)

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

        case ('!balance') | ('!bal'):
            #checks a users balance
            balance = get_balance(message.author.id)
            await message.channel.send(f'<@{message.author.id}> you have ${balance}')

        case '!joke':
            #dad joke
            await message.channel.send('Dad')
        
        case '!letslarp':
            #bossdrobots idea. No clue what it means
            await message.channel.send('just this one time')

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



        case '!getinvestment':
            user_id = message.author.id
            username = message.author.display_name
            amount = get_invested(user_id)
            await message.channel.send(f'Ooo looky, {username} has ${amount} invested. Pretty hot')

      
                
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
                    await RPS(message, client, bet)
                except ValueError:
                    await message.channel.send('I only accept MONEY as a bet. nothing else')
            else:
                await RPS(message, client)


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
            reward = random.randint(5, 50)
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            operator = random.choice(['+', '-', '*'])
            
            if operator == '+':
                answer = a + b
            elif operator == '-':
                answer = a - b
            else:
                answer = a * b
                reward *= 2  # double the reward for multiplication since it's harder
            
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
                
                update_balance(message.author.id, get_balance(message.author.id) + reward)
                await message.channel.send(f'correct! here\'s ${reward} you earned it')
            else:
                work_cooldowns[user_id] = asyncio.get_event_loop().time()
                await message.channel.send(f'WRONG. the answer was {answer}. 1 min cooldown!')                
        
        case 'six':
            await message.channel.send('seven')
        

        
        case s if s.startswith('!use'):
            await use(message, client)

        case _:
            await superuser_commands(message)
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