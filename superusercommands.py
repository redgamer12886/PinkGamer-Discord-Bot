#database setup for bank system, will add more later

import sqlite3



conn = sqlite3.connect('bank.db')
c = conn.cursor()



async def superuser_commands(message):

    match message.content:

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

        case s if s.startswith('!givemoney'):
                    if message.author.id == 585178815253446685:
                        if len(message.mentions) == 0:
                            await message.channel.send('You need to @ someone!')
                            return
                        if len(message.content.split()) < 3:
                            await message.channel.send('You need to specify an amount! Usage: !givemoney @user amount')
                            return  
                        
                        target_id = message.mentions[0].id
                        amount = message.content.split()[2]
                        c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, str(target_id)))
                        conn.commit()

                        await message.channel.send(f'Gave <@{target_id}> ${amount}')
                    else:
                        await message.channel.send('You don\'t have permission to do that!')



