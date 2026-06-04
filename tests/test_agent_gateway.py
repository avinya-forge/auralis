from fastapi.testclient import TestClient

from src.modules.agent.orchestrator import TaskDispatcher, TaskRouter
from src.modules.api.main import app

client = TestClient(app)


def test_gateway_agent_orchestration():
    """
    Integration test combining agent orchestrator logic and gateway path endpoints.
    Verifies that a request to the API correctly interfaces with the orchestrator.
    """
    # 1. API receives data
    payload = {"title": "Agent Song", "artist": "Gateway Artist", "year": 2024}
    response = client.post("/metadata", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data

    task_payload = {"id": data["id"], "action": "analyze", "data": data, "confidence_score": 0.85}

    # 2. Orchestrator processes the task
    router = TaskRouter(default_threshold=0.8)
    dispatcher = TaskDispatcher()

    is_confident = router.is_confident(task_payload["confidence_score"])

    # Confident tasks go to local, unconfident to cloud
    dispatcher.dispatch(task_payload, use_cloud=not is_confident)

    import time

    time.sleep(0.1)  # multiprocessing queue wait

    # 3. Verify it was routed locally
    local_task = dispatcher.get_local_task()
    cloud_task = dispatcher.get_cloud_task()

    assert local_task["id"] == data["id"]
    assert cloud_task == {}
