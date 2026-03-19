import numpy as np
import pytest

from src.modules.neu.embedding_database import EmbeddingDatabase


@pytest.fixture
def memory_db():
    db = EmbeddingDatabase(":memory:")
    yield db
    db.close()


def test_initialization(memory_db):
    assert memory_db.conn is not None
    # Check if table exists
    cursor = memory_db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='embeddings'")
    assert cursor.fetchone() is not None


def test_upsert_and_retrieve_embedding(memory_db):
    track_id = "test_track_1"
    vector = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
    model_version = "test-model-v1"

    memory_db.upsert_embedding(track_id, vector, model_version)

    cursor = memory_db.conn.cursor()
    cursor.execute("SELECT vector_blob, model_version FROM embeddings WHERE track_id = ?", (track_id,))
    row = cursor.fetchone()

    assert row is not None
    retrieved_blob, retrieved_model_version = row
    retrieved_vector = np.frombuffer(retrieved_blob, dtype=np.float32)

    assert retrieved_model_version == model_version
    np.testing.assert_array_almost_equal(vector, retrieved_vector)


def test_upsert_updates_existing(memory_db):
    track_id = "test_track_2"
    vector1 = np.array([0.1, 0.1], dtype=np.float32)
    vector2 = np.array([0.9, 0.9], dtype=np.float32)

    memory_db.upsert_embedding(track_id, vector1, "v1")
    memory_db.upsert_embedding(track_id, vector2, "v2")

    cursor = memory_db.conn.cursor()
    cursor.execute("SELECT vector_blob, model_version FROM embeddings WHERE track_id = ?", (track_id,))
    row = cursor.fetchone()

    assert row is not None
    retrieved_blob, retrieved_model_version = row
    retrieved_vector = np.frombuffer(retrieved_blob, dtype=np.float32)

    assert retrieved_model_version == "v2"
    np.testing.assert_array_almost_equal(vector2, retrieved_vector)


def test_search_similar(memory_db):
    # Insert some test vectors
    memory_db.upsert_embedding("track_1", np.array([1.0, 0.0, 0.0], dtype=np.float32), "v1")
    memory_db.upsert_embedding("track_2", np.array([0.0, 1.0, 0.0], dtype=np.float32), "v1")
    memory_db.upsert_embedding("track_3", np.array([0.0, 0.0, 1.0], dtype=np.float32), "v1")
    memory_db.upsert_embedding("track_4", np.array([0.8, 0.2, 0.0], dtype=np.float32), "v1")

    # Target vector very close to track_1
    target = np.array([0.9, 0.1, 0.0], dtype=np.float32)

    results = memory_db.search_similar(target, top_k=2)

    assert len(results) == 2
    # track_1 should be the most similar, followed by track_4
    assert results[0][0] == "track_1"
    assert results[1][0] == "track_4"

    # Check similarity score is returned and roughly expected
    assert isinstance(results[0][1], float)
    assert results[0][1] > 0.8  # cosine sim of [1,0,0] and [0.9,0.1,0] is high


def test_search_similar_empty_db(memory_db):
    target = np.array([1.0, 0.0], dtype=np.float32)
    results = memory_db.search_similar(target, top_k=5)
    assert len(results) == 0


def test_search_similar_different_model_versions(memory_db):
    # Should only compare embeddings with the same model version (or we might need to handle this explicitly)
    # The requirement didn't specify, but let's assume search_similar can optionally filter by model_version
    memory_db.upsert_embedding("track_1", np.array([1.0, 0.0], dtype=np.float32), "v1")
    memory_db.upsert_embedding("track_2", np.array([1.0, 0.0], dtype=np.float32), "v2")

    target = np.array([1.0, 0.0], dtype=np.float32)

    # If we filter by model_version="v1"
    results_v1 = memory_db.search_similar(target, top_k=5, model_version="v1")
    assert len(results_v1) == 1
    assert results_v1[0][0] == "track_1"
