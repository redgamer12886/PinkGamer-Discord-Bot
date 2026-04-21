
import sqlite3
import random
from unittest import case
import discord
import os
import time
import asyncio





async def help_command(message):

    parts = message.content.split()
                
    if len(parts) == 1:
                    # general help page
                    await message.channel.send("""Available commands: 
            !help, !hello, !joke, !letslarp, !quote, !8ball, !uwu, !mommyasmr, !daddyasmr, !roll, !guessroll, !rps, !blackjack, !balance, !beg, !donate, !invest, !getinvestment, !sellinvested, !leaderboard, !work, @me (PinkGamer), penis, die, expensive, mcdonald, 6, goodnight, !shop, !buy, !inventory, !use
SUPERUSER COMMANDS: only Alex/Redgamer can use those:
            !fixuser, !givemoney
                                                
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
Related Commands: !invest, !getinvestment, !blackjack, !work""")
                            
            case 'getinvestment':
                await message.channel.send("""**!getinvestment** - tells you how much money you have invested
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
                


