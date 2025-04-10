# db.py — хранение статистики, проверка премиума и админов
import sqlite3
from datetime import datetime, timedelta

DB_NAME = "bot_users.db"

# Администраторы с вечным премиумом
ADMIN_IDS = [954645592]  # ← оставляем только одного админа

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    request_count INTEGER DEFAULT 0,
                    premium_until TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                    user_id INTEGER,
                    timestamp TEXT,
                    content TEXT
                )''')
    conn.commit()
    conn.close()

def increment_request(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, request_count) VALUES (?, 0)", (user_id,))
    c.execute("UPDATE users SET request_count = request_count + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT request_count, premium_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row if row else (0, None)

def is_premium(user_id):
    if user_id in ADMIN_IDS:
        return True
    count, premium_until = get_user(user_id)
    if premium_until:
        return datetime.fromisoformat(premium_until) > datetime.now()
    return False

def set_premium(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    expires = (datetime.now() + timedelta(days=7)).isoformat()
    c.execute("INSERT OR REPLACE INTO users (user_id, request_count, premium_until) VALUES (?, COALESCE((SELECT request_count FROM users WHERE user_id = ?), 0), ?)", (user_id, user_id, expires))
    conn.commit()
    conn.close()

    with open("premium_users.txt", "a", encoding="utf-8") as f:
        f.write(f"{user_id} → до {expires}\n")

def save_article(user_id, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO history (user_id, timestamp, content) VALUES (?, ?, ?)", (user_id, datetime.now().isoformat(), content))
    conn.commit()
    conn.close()

def get_history(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT timestamp, content FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows
