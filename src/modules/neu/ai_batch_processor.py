import logging
import multiprocessing
import queue
import time
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class AIBatchProcessor:
    """
    Handles batched AI tasks via multiprocessing.Queue to prevent UI freezes.
    """

    def __init__(self, num_workers: int = 1):
        self._task_queue = multiprocessing.Queue()
        self._result_queue = multiprocessing.Queue()
        self._stop_event = multiprocessing.Event()
        self._workers = []
        self._num_workers = num_workers
        self._start_workers()

    def _start_workers(self):
        """Starts background worker processes."""
        for _ in range(self._num_workers):
            p = multiprocessing.Process(
                target=self._worker_loop,
                args=(self._task_queue, self._result_queue, self._stop_event),
            )
            p.daemon = True
            p.start()
            self._workers.append(p)

    @staticmethod
    def _worker_loop(
        task_queue: multiprocessing.Queue,
        result_queue: multiprocessing.Queue,
        stop_event: multiprocessing.Event,
    ):
        """Dedicated background worker to process tracks."""
        while not stop_event.is_set():
            try:
                task = task_queue.get(timeout=0.1)
                # Task format expected: (task_id, path, model_inference_callable)
                if task is None:
                    continue

                task_id, path, inference_callable = task
                try:
                    result = inference_callable(path)
                    result_queue.put((task_id, path, result, None))
                except Exception as e:
                    logger.error(f"Error processing {path}: {e}")
                    result_queue.put((task_id, path, None, str(e)))

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Unexpected worker error: {e}")

    def enqueue_track(self, path: str, inference_callable: Callable) -> str:
        """
        Enqueues a track for processing.
        Returns a task_id for tracking.
        """
        task_id = str(time.time()) + "_" + path
        self._task_queue.put((task_id, path, inference_callable))
        return task_id

    def get_results(self) -> List[Dict[str, Any]]:
        """
        Retrieves all currently available results from the result queue.
        Returns a list of dicts containing task_id, path, result, and error.
        """
        results = []
        while not self._result_queue.empty():
            try:
                task_id, path, result, error = self._result_queue.get_nowait()
                results.append({"task_id": task_id, "path": path, "result": result, "error": error})
            except queue.Empty:
                break
        return results

    def terminate(self):
        """Stops all background workers."""
        self._stop_event.set()
        for p in self._workers:
            p.join(timeout=1.0)
            if p.is_alive():
                p.terminate()
        self._workers.clear()

    def __del__(self):
        self.terminate()
