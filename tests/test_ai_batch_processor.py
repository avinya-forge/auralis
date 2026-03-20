import pytest
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
        task_id1 = processor.enqueue_track("/path/to/track1.mp3", mock_inference_success)
        task_id2 = processor.enqueue_track("/path/to/track2.mp3", mock_inference_success)

        results = []
        for _ in range(20): # Wait up to 2 seconds
            results.extend(processor.get_results())
            if len(results) == 2:
                break
            time.sleep(0.1)

        assert len(results) == 2

        # Verify content
        paths = [res['path'] for res in results]
        assert "/path/to/track1.mp3" in paths
        assert "/path/to/track2.mp3" in paths

        for res in results:
            assert res['error'] is None
            assert res['result'] == f"Processed {res['path']}"
    finally:
        processor.terminate()

def test_batch_processor_failure():
    processor = AIBatchProcessor(num_workers=1)
    try:
        task_id = processor.enqueue_track("/path/to/bad_track.mp3", mock_inference_failure)

        results = []
        for _ in range(20):
            results.extend(processor.get_results())
            if len(results) == 1:
                break
            time.sleep(0.1)

        assert len(results) == 1
        res = results[0]
        assert res['path'] == "/path/to/bad_track.mp3"
        assert res['result'] is None
        assert "Failed to process" in res['error']
    finally:
        processor.terminate()

def test_batch_processor_terminate():
    processor = AIBatchProcessor(num_workers=1)
    processor.terminate()
    assert len(processor._workers) == 0
