from fastapi.testclient import TestClient

from src.modules.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "x-process-time" in response.headers


def test_create_and_get_metadata():
    payload = {"title": "Test Song", "artist": "Test Artist", "year": 2023}
    response = client.post("/metadata", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Song"
    assert "id" in data

    item_id = data["id"]

    get_response = client.get(f"/metadata/{item_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["id"] == item_id
    assert get_data["artist"] == "Test Artist"


def test_get_metadata_not_found():
    response = client.get("/metadata/invalid-id")
    assert response.status_code == 404


def test_stream_audio_unauthorized():
    response = client.get("/sync/audio/test-file")
    assert response.status_code == 403 or response.status_code == 401  # Missing credentials


def test_stream_audio_invalid_token():
    response = client.get(
        "/sync/audio/test-file", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401


def test_stream_audio_authorized():
    response = client.get(
        "/sync/audio/test-file", headers={"Authorization": "Bearer valid-jwt-token"}
    )
    assert response.status_code == 200
    assert response.content == b"fake audio data"
    assert response.headers["content-type"] == "audio/mpeg"
