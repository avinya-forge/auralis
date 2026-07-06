from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from jose import jwt

from src.modules.api.main import ALGORITHM, SECRET_KEY, app

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
    # Generate a valid token
    to_encode = {"sub": "admin", "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}
    valid_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(
        "/sync/audio/test-file", headers={"Authorization": f"Bearer {valid_token}"}
    )
    assert response.status_code == 200
    assert response.content == b"fake audio data"
    assert response.headers["content-type"] == "audio/mpeg"


def test_stream_audio_expired_token():
    # Generate an expired token
    to_encode = {"sub": "admin", "exp": datetime.now(timezone.utc) - timedelta(minutes=15)}
    expired_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(
        "/sync/audio/test-file", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401


def test_login_success():
    response = client.post("/login", json={"username": "admin", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure():
    response = client.post("/login", json={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401


def test_rate_limiting_metadata_post():
    from src.modules.api.main import limiter

    payload = {"title": "Test Song", "artist": "Test Artist", "year": 2023}

    # Reset limiter for this test
    limiter.reset()

    # The limit is 10/minute, so we make 10 requests to reach the limit.
    for _ in range(10):
        response = client.post("/metadata", json=payload)
        assert response.status_code == 200

    # The 11th request overall should be rate limited
    response = client.post("/metadata", json=payload)
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text
