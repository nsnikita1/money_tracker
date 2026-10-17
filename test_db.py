from datetime import datetime, timezone

import db


def test_users_are_isolated(clean_db):
    db.add_expense(1, 10000, 'еда')
    db.add_expense(2, 5000, 'транспорт')
    assert db.get_month_total(1) == 10000
    assert db.get_month_total(2) == 5000


def test_history_only_own(clean_db):
    db.add_expense(1, 10000, 'еда')
    db.add_expense(2, 5000, 'транспорт')
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    rows = db.get_history(1, today)
    assert len(rows) == 1
    assert rows[0][1] == 'еда'


def test_income_not_mixed_with_expense(clean_db):
    db.add_expense(1, 10000, 'еда')
    db.add_expense(1, 50000, 'зарплата', type='income')
    assert db.get_month_total(1, type='expense') == 10000
    assert db.get_month_total(1, type='income') == 50000


def test_month_balance(clean_db):
    db.add_expense(1, 10000, 'еда')
    db.add_expense(1, 50000, 'зарплата', type='income')
    assert db.get_month_balance(1) == 40000