import sqlite3
import os

DB_PATH = "game.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 0,
            active_skin TEXT DEFAULT 'Beige'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS skins (
            name TEXT PRIMARY KEY,
            unlocked INTEGER DEFAULT 0,
            price INTEGER DEFAULT 0
        )
    """)

    try:
        cur.execute("ALTER TABLE player ADD COLUMN death_screen_enabled INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    cur.execute("SELECT COUNT(*) FROM player")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO player (coins, active_skin, death_screen_enabled) VALUES (?, ?, ?)", (0, "Beige", 1))

    cur.execute("SELECT COUNT(*) FROM skins")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO skins (name, unlocked, price) VALUES (?, ?, ?)", ("Beige", 1, 0))
        cur.execute("INSERT INTO skins (name, unlocked, price) VALUES (?, ?, ?)", ("Blue", 0, 50))
        cur.execute("INSERT INTO skins (name, unlocked, price) VALUES (?, ?, ?)", ("Green", 0, 50))

    conn.commit()
    conn.close()

def get_player_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT coins, active_skin, death_screen_enabled FROM player WHERE id=1")
    row = cur.fetchone()
    conn.close()
    return {"coins": row[0], "active_skin": row[1], "death_screen_enabled": bool(row[2])}

def set_active_skin(skin_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE player SET active_skin = ? WHERE id=1", (skin_name,))
    conn.commit()
    conn.close()

def get_skins():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, unlocked, price FROM skins")
    rows = cur.fetchall()
    conn.close()
    return [{"name": r[0], "unlocked": bool(r[1]), "price": r[2]} for r in rows]

def buy_skin(skin_name):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT price FROM skins WHERE name = ?", (skin_name,))
    price = cur.fetchone()[0]
    cur.execute("SELECT coins FROM player WHERE id=1")
    coins = cur.fetchone()[0]
    if coins >= price:
        cur.execute("UPDATE player SET coins = coins - ? WHERE id=1", (price,))
        cur.execute("UPDATE skins SET unlocked = 1 WHERE name = ?", (skin_name,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def add_coins(amount):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE player SET coins = coins + ? WHERE id=1", (amount,))
    conn.commit()
    conn.close()

def get_coins():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT coins FROM player WHERE id=1")
    coins = cur.fetchone()[0]
    conn.close()
    return coins

def set_death_screen(enabled):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE player SET death_screen_enabled = ? WHERE id=1", (int(enabled),))
    conn.commit()
    conn.close()