from unittest.mock import MagicMock, patch


from src.modules.id.cleanup import init_play_history_schema, prune_play_history


@patch("src.modules.id.cleanup.get_db_connection")
def test_init_play_history_schema(mock_get_db):
    mock_conn = MagicMock()
    mock_get_db.return_value.__enter__.return_value = mock_conn
    init_play_history_schema("dummy.db")
    mock_conn.execute.assert_called_once()
    assert "CREATE TABLE IF NOT EXISTS play_history" in mock_conn.execute.call_args[0][0]


@patch("src.modules.id.cleanup.get_db_connection")
def test_prune_play_history(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 5
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value.__enter__.return_value = mock_conn

    deleted = prune_play_history("dummy.db", 365)

    assert deleted == 5
    mock_cursor.execute.assert_called_once()
    assert "DELETE FROM play_history WHERE played_at < ?" in mock_cursor.execute.call_args[0][0]
