import datetime
import sqlite3

from src.modules.api.cleanup import prune_expired_tokens


def test_prune_expired_tokens(tmp_path):
    db_path = str(tmp_path / "test_sessions.db")

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE sessions (
            id TEXT PRIMARY KEY,
            token TEXT,
            expires_at TEXT
        )
    """)

    now = datetime.datetime.now()
    past = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%f")
    future = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%f")

    conn.execute("INSERT INTO sessions VALUES (?, ?, ?)", ("1", "token1", past))
    conn.execute("INSERT INTO sessions VALUES (?, ?, ?)", ("2", "token2", future))
    conn.commit()
    conn.close()

    deleted = prune_expired_tokens(db_path)

    assert deleted == 1

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sessions")
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) == 1
    assert rows[0][0] == "2"


def test_prune_expired_tokens_error(tmp_path):
    # Pass an invalid db path or a directory to trigger an error
    db_path = str(tmp_path)

    deleted = prune_expired_tokens(db_path)
    assert deleted == 0
