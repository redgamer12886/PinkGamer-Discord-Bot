import sqlite3
import random
import discord
import os
import time
import asyncio



# importing from other files ive writen for better organization.
from database import update_balance, get_balance



# updates bal if user lost
def loose(user, bet):
    update_balance(user, get_balance(user) - bet)

# updates bal if user won
def win(user, bet):
    update_balance(user, get_balance(user) + bet)


# Rock paper scissors game with betting
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


# Strickty for use in blackjack function
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



# Blackjack function
async def blackjack(message, client, bet=None):

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

# rolls a d20
def roll():
    result = random.randint(1, 20)
    return result