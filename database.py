import sqlite3
import random
import discord
import os
import time
import asyncio







#database setup for bank system, will add more later
conn = sqlite3.connect('bank.db')
c = conn.cursor()


def setup_database():
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






# returns the balance of the user_id spesificed from the database, if the user_id does not exist it creates a new entry with a balance of 100 and returns 100
def get_balance(user_id):
    c.execute('SELECT balance FROM users WHERE user_id = ?', (str(user_id),))
    result = c.fetchone()
    if result is None:
        c.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (str(user_id), 100))
        conn.commit()
        return 100
    return result[0]


#update bal of the given user_id, by the given amount.
def update_balance(user_id, amount):
    c.execute('UPDATE users SET balance = ? WHERE user_id = ?', (amount, str(user_id)))
    conn.commit()

# gets the amount the user has invested
def get_invested(user_id):
    c.execute('SELECT invested FROM users WHERE user_id = ?', (str(user_id),))
    result = c.fetchone()

    if result is None:
        return 0
    return result[0]


# updates invested amount for user
def update_invested(user_id, amount):
    c.execute('UPDATE users SET invested = ? WHERE user_id = ?', (int(amount), str(user_id)))
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

