from src.modules.agent.orchestrator import TaskDispatcher, TaskRouter


def test_task_router_is_confident():
    router = TaskRouter(default_threshold=0.8)

    assert router.is_confident(0.9) is True
    assert router.is_confident(0.8) is True
    assert router.is_confident(0.7) is False
    assert router.is_confident(0.5, threshold=0.4) is True
    assert router.is_confident(None) is False


def test_task_dispatcher():
    dispatcher = TaskDispatcher()

    task1 = {"id": 1, "data": "local_task"}
    task2 = {"id": 2, "data": "cloud_task"}

    dispatcher.dispatch(task1, use_cloud=False)
    dispatcher.dispatch(task2, use_cloud=True)

    import time

    time.sleep(0.1)  # multiprocessing queues need a tiny bit of time

    local_task = dispatcher.get_local_task()
    cloud_task = dispatcher.get_cloud_task()

    assert local_task == task1
    assert cloud_task == task2

    # queues should be empty now
    assert dispatcher.get_local_task() == {}
    assert dispatcher.get_cloud_task() == {}
