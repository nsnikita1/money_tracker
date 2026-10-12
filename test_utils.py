import pytest
from utils import parse_amount, format_money
from datetime import datetime, timezone
import db

def test_parse_amount():
    assert parse_amount('500') == 50000
    assert parse_amount('500.50') == 50050
    assert parse_amount('0.01') == 1

@pytest.mark.parametrize(
    'bad',
    ['abc', '0', '-5', 'nan']
)
def test_parse_amount_fails(bad):
    with pytest.raises(ValueError):
        parse_amount(bad)

def test_format_money():
    assert format_money(500) == '5.00'
    assert format_money(50050) == '500.50'
    assert format_money(5) == '0.05'

def test_history_only_own(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_NAME', str(tmp_path / 'test.db'))
    db.init_db()
    db.add_expense(1, 1000, "food")
    db.add_expense(2, 14000, "transport")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = db.get_history(1, today)
    assert len(rows) == 1
    assert rows[0][1] == 'food'