import sqlite3
import random
import discord
import os
import time
import asyncio

from database import add_item, c, conn, get_balance, get_item_quantity, get_item_quantity, remove_item, update_balance


#prints out user inventory
async def inventory(message, client):
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

#prints everything in the shop
async def shop(message, client):
      # get all items from the shop
            c.execute('SELECT item_id, name, price, description FROM items')
            items = c.fetchall()
            
            shop = '🏪 **Shop** 🏪\n'
            for item_id, name, price, description in items:
                shop += f'**{name}** - ${price}\n{description}\n\n'
            
            await message.channel.send(shop)



#buys whatever item it is you want
async def buy(message, client):
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


#use an item in your inventory, ALSO stores functionality for items
async def use(message, client):
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
                await message.channel.send(f'they had a lock! your lockpick broke and their lock was used up. {client.get_user(int(target_id))} is safe... this time')
                return
                    
            # steal a random % of their balance
            target_balance = get_balance(target_id)
            if target_balance == 0:
                await message.channel.send('they\'re broke, nothing to steal!')
                return



            steal_percent = random.randint(10, 30)
            stolen = int(target_balance * (steal_percent / 100))
                    
            remove_item(user_id, 1)
            update_balance(target_id, target_balance - stolen)
            update_balance(user_id, get_balance(user_id) + stolen)
            await message.channel.send(f'you stole ${stolen} ({steal_percent}%) from {client.get_user(int(target_id))}! 😈')

        case _:
            await message.channel.send(f'no item called {item_name}')