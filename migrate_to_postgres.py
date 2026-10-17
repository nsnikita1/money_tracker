import os
import sqlite3
from datetime import datetime

import psycopg
from dotenv import load_dotenv

from db import init_db

load_dotenv()

SQLITE_PATH = os.getenv('DB_PATH', 'bot.db')

src = sqlite3.connect(SQLITE_PATH)
rows = src.execute(
    'SELECT user_id, amount, category, comment, created_at FROM expenses ORDER BY id'
).fetchall()
src.close()
print(f'В SQLite строк: {len(rows)}')

init_db()

with psycopg.connect(os.environ['DATABASE_URL']) as dst:
    count = dst.execute('SELECT COUNT(*) FROM expenses').fetchone()[0]
    if count > 0:
        raise SystemExit('В PostgreSQL уже есть данные, перенос остановлен')

    for user_id, amount, category, comment, created_at in rows:
        dst.execute(
            'INSERT INTO expenses (user_id, amount, category, comment, created_at) '
            'VALUES (%s, %s, %s, %s, %s)',
            (user_id, amount, category, comment, datetime.fromisoformat(created_at)),
        )

print('Перенос завершён')