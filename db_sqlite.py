import os
import sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv('DB_PATH', 'bot.db')


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                category TEXT NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL
            )
        ''')


def add_expense(user_id, amount, category, comment=''):
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            'INSERT INTO expenses (user_id, amount, category, comment, created_at) '
            'VALUES (?, ?, ?, ?, ?)',
            (user_id, amount, category, comment, created_at),
        )


def get_month_total(user_id):
    prefix = datetime.now(timezone.utc).strftime('%Y-%m') + '%'
    with get_connection() as conn:
        row = conn.execute(
            'SELECT COALESCE(SUM(amount), 0) FROM expenses '
            'WHERE user_id = ? AND created_at LIKE ?',
            (user_id, prefix),
        ).fetchone()
    return row[0]


def get_history(user_id, date_str):
    with get_connection() as conn:
        return conn.execute(
            'SELECT amount, category, comment, created_at FROM expenses '
            'WHERE user_id = ? AND created_at LIKE ? ORDER BY created_at',
            (user_id, date_str + '%'),
        ).fetchall()

def count_today(user_id):
    prefix = datetime.now(timezone.utc).strftime('%Y-%m-%d') + '%'
    with get_connection() as conn:
        row = conn.execute(
            'SELECT COUNT(*) FROM expenses '
            'WHERE user_id = ? AND created_at LIKE ?',
            (user_id, prefix),
        ).fetchone()
    return row[0]