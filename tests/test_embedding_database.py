from unittest.mock import patch
import sqlite3
import pytest
import numpy as np
from src.modules.neu.embedding_database import EmbeddingDatabase


@pytest.fixture
def temp_db(tmp_path):
    """Fixture to provide a temporary database path."""
    db_path = tmp_path / "test_embeddings.db"
    return str(db_path)


@pytest.fixture
def db(temp_db):
    """Fixture to provide an EmbeddingDatabase instance."""
    return EmbeddingDatabase(db_path=temp_db)


def test_init_db(temp_db):
    """Test database initialization creates the table."""
    EmbeddingDatabase(db_path=temp_db)

    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='embeddings'")
        assert cursor.fetchone() is not None


def test_upsert_and_get_embedding(db):
    """Test upserting an embedding and retrieving it."""
    track_id = "test_track_1"
    vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    model_version = "v1"

    db.upsert_embedding(track_id, vector, model_version)

    retrieved_vector = db.get_embedding(track_id)
    assert retrieved_vector is not None
    assert np.array_equal(vector, retrieved_vector)

    # Test update
    new_vector = np.array([0.4, 0.5, 0.6], dtype=np.float32)
    db.upsert_embedding(track_id, new_vector, "v2")

    retrieved_new_vector = db.get_embedding(track_id)
    assert np.array_equal(new_vector, retrieved_new_vector)


def test_get_embedding_not_found(db):
    """Test retrieving a non-existent embedding."""
    assert db.get_embedding("non_existent") is None


def test_search_similar(db):
    """Test cosine similarity search."""
    # Insert some vectors
    # v1 is [1, 0, 0]
    db.upsert_embedding("track_1", np.array([1.0, 0.0, 0.0]), "v1")
    # v2 is [0, 1, 0]
    db.upsert_embedding("track_2", np.array([0.0, 1.0, 0.0]), "v1")
    # v3 is [1, 1, 0]
    db.upsert_embedding("track_3", np.array([1.0, 1.0, 0.0]), "v1")

    # Search target is [1, 0, 0]
    target = np.array([1.0, 0.0, 0.0])

    results = db.search_similar(target, top_k=3)

    assert len(results) == 3
    # track_1 should be perfectly similar (score 1.0)
    assert results[0][0] == "track_1"
    assert np.isclose(results[0][1], 1.0)

    # track_3 should be next
    assert results[1][0] == "track_3"
    assert results[1][1] > 0.0

    # track_2 should be orthogonal (score 0.0)
    assert results[2][0] == "track_2"
    assert np.isclose(results[2][1], 0.0)


def test_search_similar_with_model_filter(db):
    """Test searching with model_version filter."""
    db.upsert_embedding("track_1", np.array([1.0, 0.0, 0.0]), "v1")
    db.upsert_embedding("track_2", np.array([1.0, 0.0, 0.0]), "v2")

    target = np.array([1.0, 0.0, 0.0])

    # Filter for v1
    results_v1 = db.search_similar(target, model_version="v1")
    assert len(results_v1) == 1
    assert results_v1[0][0] == "track_1"

    # Filter for v2
    results_v2 = db.search_similar(target, model_version="v2")
    assert len(results_v2) == 1
    assert results_v2[0][0] == "track_2"


def test_search_similar_zero_norm_target(db):
    """Test searching with a zero norm target."""
    db.upsert_embedding("track_1", np.array([1.0, 0.0, 0.0]), "v1")
    target = np.array([0.0, 0.0, 0.0])

    results = db.search_similar(target)
    assert len(results) == 0


def test_search_similar_zero_norm_stored(db):
    """Test searching when a stored vector has zero norm."""
    db.upsert_embedding("track_zero", np.array([0.0, 0.0, 0.0]), "v1")
    db.upsert_embedding("track_valid", np.array([1.0, 0.0, 0.0]), "v1")

    target = np.array([1.0, 0.0, 0.0])

    results = db.search_similar(target)
    assert len(results) == 1
    assert results[0][0] == "track_valid"


def test_init_db_error(temp_db):
    """Test database initialization error handling."""
    with patch("sqlite3.connect", side_effect=sqlite3.Error("Mocked error")):
        with pytest.raises(sqlite3.Error):
            EmbeddingDatabase(db_path=temp_db)


def test_upsert_embedding_error(db):
    """Test upsert_embedding error handling."""
    with patch("sqlite3.connect", side_effect=sqlite3.Error("Mocked error")):
        with pytest.raises(sqlite3.Error):
            db.upsert_embedding("track_err", np.array([1.0], dtype=np.float32), "v1")

    with pytest.raises(Exception):
        # Pass a primitive int which doesn't have astype()
        db.upsert_embedding("track_err", 123, "v1")


def test_get_embedding_error(db):
    """Test get_embedding error handling."""
    with patch("sqlite3.connect", side_effect=sqlite3.Error("Mocked error")):
        result = db.get_embedding("track_err")
        assert result is None


def test_search_similar_error(db):
    """Test search_similar error handling."""
    target = np.array([1.0], dtype=np.float32)
    with patch("sqlite3.connect", side_effect=sqlite3.Error("Mocked error")):
        result = db.search_similar(target)
        assert result == []

    # Pass a primitive int which doesn't have astype()
    result = db.search_similar(123)
    assert result == []
