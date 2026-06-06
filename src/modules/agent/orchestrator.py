import logging
import multiprocessing
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TaskDispatcher:
    """
    Dispatcher for routing tasks to local vs cloud queues.
    """

    def __init__(self):
        self.local_queue = multiprocessing.Queue()
        self.cloud_queue = multiprocessing.Queue()

    def dispatch(self, task: Dict[str, Any], use_cloud: bool = False) -> None:
        """
        Dispatch a task to the appropriate queue.
        """
        if use_cloud:
            self.cloud_queue.put(task)
            logger.info(f"Dispatched task {task.get('id', 'unknown')} to cloud queue.")
        else:
            self.local_queue.put(task)
            logger.info(f"Dispatched task {task.get('id', 'unknown')} to local queue.")

    def get_local_task(self) -> Dict[str, Any]:
        """Get a task from the local queue."""
        import queue

        try:
            task: Dict[str, Any] = self.local_queue.get_nowait()
            return task
        except queue.Empty:
            return {}

    def get_cloud_task(self) -> Dict[str, Any]:
        """Get a task from the cloud queue."""
        import queue

        try:
            task: Dict[str, Any] = self.cloud_queue.get_nowait()
            return task
        except queue.Empty:
            return {}


class TaskRouter:
    """
    Router for evaluating tasks against AI models or local models.
    """

    def __init__(self, default_threshold: float = 0.8):
        self.default_threshold = default_threshold

    def is_confident(
        self, confidence_score: Optional[float], threshold: Optional[float] = None
    ) -> bool:
        """
        Compare confidence score against threshold.
        Returns True if score >= threshold, False otherwise.
        """
        if threshold is None:
            threshold = self.default_threshold

        if confidence_score is None:
            return False

        return confidence_score >= threshold
