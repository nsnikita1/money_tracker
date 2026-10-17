import os
from datetime import datetime, timedelta, timezone

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg.connect(os.environ['DATABASE_URL'])


def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                amount BIGINT NOT NULL,
                category TEXT NOT NULL,
                comment TEXT,
                type TEXT NOT NULL DEFAULT 'expense',
                created_at TIMESTAMPTZ NOT NULL
            )
        ''')
        conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_expenses_user_date '
            'ON expenses (user_id, created_at)'
        )


def add_expense(user_id, amount, category, comment='', type='expense'):
    with get_connection() as conn:
        conn.execute(
            'INSERT INTO expenses (user_id, amount, category, comment, type, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s)',
            (user_id, amount, category, comment, type, datetime.now(timezone.utc)),
        )


def month_range(now=None):
    now = now or datetime.now(timezone.utc)
    start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    if now.month == 12:
        end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
    return start, end


def get_month_total(user_id, type='expense'):
    start, end = month_range()
    with get_connection() as conn:
        row = conn.execute(
            'SELECT COALESCE(SUM(amount), 0) FROM expenses '
            'WHERE user_id = %s AND type = %s AND created_at >= %s AND created_at < %s',
            (user_id, type, start, end),
        ).fetchone()
    return int(row[0])


def get_month_balance(user_id):
    income = get_month_total(user_id, type='income')
    expense = get_month_total(user_id, type='expense')
    return income - expense


def get_history(user_id, date_str, type=None):
    start = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    with get_connection() as conn:
        if type is None:
            return conn.execute(
                'SELECT amount, category, comment, type, created_at FROM expenses '
                'WHERE user_id = %s AND created_at >= %s AND created_at < %s '
                'ORDER BY created_at',
                (user_id, start, end),
            ).fetchall()
        return conn.execute(
            'SELECT amount, category, comment, type, created_at FROM expenses '
            'WHERE user_id = %s AND type = %s AND created_at >= %s AND created_at < %s '
            'ORDER BY created_at',
            (user_id, type, start, end),
        ).fetchall()


def count_today(user_id):
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    with get_connection() as conn:
        row = conn.execute(
            'SELECT COUNT(*) FROM expenses '
            'WHERE user_id = %s AND created_at >= %s AND created_at < %s',
            (user_id, start, end),
        ).fetchone()
    return row[0]