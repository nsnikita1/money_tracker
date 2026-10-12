import db

def test_users_are_isolated(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_NAME', str(tmp_path / 'test.db'))
    db.init_db()
    db.add_expense(1, 10000, 'еда')
    db.add_expense(2, 5000, 'транспорт')
    assert db.get_month_total(1) == 10000
    assert db.get_month_total(2) == 5000