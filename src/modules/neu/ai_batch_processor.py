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

    def __init__(self, num_workers: int = 1, task_timeout: float = 300.0):
        self._manager = multiprocessing.Manager()
        self._task_queue: multiprocessing.Queue = multiprocessing.Queue()
        self._result_queue: multiprocessing.Queue = multiprocessing.Queue()
        self._stop_event: Any = multiprocessing.Event()
        self._active_tasks = self._manager.dict()
        self._workers: List[multiprocessing.Process] = []
        self._num_workers = num_workers
        self._task_timeout = task_timeout
        self._enqueued_tasks: Dict[str, Dict[str, Any]] = {}
        self._start_workers()

    def _start_workers(self):
        """Starts background worker processes."""
        self._stop_event.clear()
        for _ in range(self._num_workers):
            p = multiprocessing.Process(
                target=self._worker_loop,
                args=(self._task_queue, self._result_queue, self._stop_event, self._active_tasks),
            )
            p.daemon = True
            p.start()
            self._workers.append(p)

    @staticmethod
    def _worker_loop(
        task_queue: multiprocessing.Queue,
        result_queue: multiprocessing.Queue,
        stop_event: Any,
        active_tasks: Dict[str, float]
    ):
        """Dedicated background worker to process tracks."""
        while not stop_event.is_set():
            try:
                task = task_queue.get(timeout=0.1)
                # Task format expected: (task_id, path, model_inference_callable)
                if task is None:
                    continue

                task_id, path, inference_callable = task
                active_tasks[task_id] = time.time()
                try:
                    result = inference_callable(path)
                    result_queue.put((task_id, path, result, None))
                except Exception as e:
                    logger.error(f"Error processing {path}: {e}")
                    result_queue.put((task_id, path, None, str(e)))
                finally:
                    active_tasks.pop(task_id, None)

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
        self._enqueued_tasks[task_id] = {"path": path}
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
                if task_id in self._enqueued_tasks:
                    del self._enqueued_tasks[task_id]
                results.append({"task_id": task_id, "path": path, "result": result, "error": error})
            except queue.Empty:
                break
        return results

    def recover_stuck_tasks(self):
        """Detects stuck tasks, pushes error results, and restarts workers."""
        current_time = time.time()
        active_items = dict(self._active_tasks)
        stuck_task_ids = [
            t_id for t_id, start_time in active_items.items()
            if current_time - start_time > self._task_timeout
        ]

        if not stuck_task_ids:
            return

        for t_id in stuck_task_ids:
            self._active_tasks.pop(t_id, None)
            info = self._enqueued_tasks.pop(t_id, None)
            path = info["path"] if info else "unknown"
            logger.error(f"Task {t_id} for path {path} timed out.")
            self._result_queue.put((t_id, path, None, "Task timed out"))

        remaining_active = dict(self._active_tasks)
        for t_id in remaining_active.keys():
            self._active_tasks.pop(t_id, None)
            info = self._enqueued_tasks.pop(t_id, None)
            path = info["path"] if info else "unknown"
            logger.error(f"Task {t_id} for path {path} aborted due to worker restart.")
            self._result_queue.put((t_id, path, None, "Task aborted due to worker restart"))

        logger.info("Restarting workers due to stuck tasks.")
        self.terminate()
        self._start_workers()

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
