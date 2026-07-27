import queue
import time

from src.modules.neu.ai_batch_processor import AIBatchProcessor


def mock_inference_success(path):
    # Simulate work
    time.sleep(0.1)
    return f"Processed {path}"


def mock_inference_failure(path):
    time.sleep(0.1)
    raise ValueError(f"Failed to process {path}")


def test_batch_processor_success():
    processor = AIBatchProcessor(num_workers=1)
    try:
        processor.enqueue_track("/path/to/track1.mp3", mock_inference_success)
        processor.enqueue_track("/path/to/track2.mp3", mock_inference_success)

        results = []
        for _ in range(20):  # Wait up to 2 seconds
            results.extend(processor.get_results())
            if len(results) == 2:
                break
            time.sleep(0.1)

        assert len(results) == 2

        # Verify content
        paths = [res["path"] for res in results]
        assert "/path/to/track1.mp3" in paths
        assert "/path/to/track2.mp3" in paths

        for res in results:
            assert res["error"] is None
            assert res["result"] == f"Processed {res['path']}"
    finally:
        processor.terminate()


def test_batch_processor_failure():
    processor = AIBatchProcessor(num_workers=1)
    try:
        processor.enqueue_track("/path/to/bad_track.mp3", mock_inference_failure)

        results = []
        for _ in range(20):
            results.extend(processor.get_results())
            if len(results) == 1:
                break
            time.sleep(0.1)

        assert len(results) == 1
        res = results[0]
        assert res["path"] == "/path/to/bad_track.mp3"
        assert res["result"] is None
        assert "Failed to process" in res["error"]
    finally:
        processor.terminate()


def test_batch_processor_terminate():
    processor = AIBatchProcessor(num_workers=1)
    processor.terminate()
    assert len(processor._workers) == 0


def test_batch_processor_worker_loop():
    from unittest.mock import MagicMock

    task_queue = MagicMock()
    result_queue = MagicMock()
    stop_event = MagicMock()

    # We want the loop to run several times to hit all branches
    stop_event.is_set.side_effect = [False, False, False, False, True]

    # 1. Success task
    # 2. None task
    # 3. Task causing general exception
    # 4. queue.Empty
    task_queue.get.side_effect = [
        ("task_1", "/path/to/loop_track.mp3", mock_inference_success),
        None,
        ValueError("Boom"),
        queue.Empty,
    ]

    AIBatchProcessor._worker_loop(task_queue, result_queue, stop_event)

    # Verify result queue received the success result
    result_queue.put.assert_called_once_with(
        ("task_1", "/path/to/loop_track.mp3", "Processed /path/to/loop_track.mp3", None)
    )


def test_batch_processor_worker_loop_inference_error():
    from unittest.mock import MagicMock

    task_queue = MagicMock()
    result_queue = MagicMock()
    stop_event = MagicMock()

    stop_event.is_set.side_effect = [False, True]

    def failing_callable(path):
        raise ValueError("Inference failed")

    task_queue.get.side_effect = [("task_2", "/path/to/fail_track.mp3", failing_callable)]

    AIBatchProcessor._worker_loop(task_queue, result_queue, stop_event)
    result_queue.put.assert_called_once_with(
        ("task_2", "/path/to/fail_track.mp3", None, "Inference failed")
    )


def test_batch_processor_get_results_empty():

    processor = AIBatchProcessor(num_workers=0)
    processor._result_queue.empty = lambda: False

    def raise_empty():
        raise queue.Empty

    processor._result_queue.get_nowait = raise_empty

    results = processor.get_results()
    assert results == []


def test_batch_processor_terminate_alive():
    from unittest.mock import MagicMock

    processor = AIBatchProcessor(num_workers=0)
    mock_process = MagicMock()
    mock_process.is_alive.return_value = True
    processor._workers.append(mock_process)

    processor.terminate()
    mock_process.terminate.assert_called_once()
