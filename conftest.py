import os

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def clean_db(monkeypatch):
    url = os.environ['TEST_DATABASE_URL']
    assert 'test' in url, 'Тесты нельзя запускать на рабочей базе'
    monkeypatch.setenv('DATABASE_URL', url)
    import db
    db.init_db()
    with db.get_connection() as conn:
        conn.execute('TRUNCATE expenses')