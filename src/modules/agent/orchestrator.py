import hashlib
import logging
import multiprocessing
import random
import re
from typing import Any, Dict, Optional

from src.modules.agent.task_observer import TaskObserver
from src.services.ai.llm_orchestrator import LLMOrchestrator

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


class MetaAgentTaskRouter:
    def __init__(self, llm_bridge: LLMOrchestrator):
        self.llm_bridge = llm_bridge
        self.registered_agents: Dict[str, list] = {}
        self.task_observer = TaskObserver()

    def register_agent(self, role: str, capabilities: list):
        """Register an agent with specific capabilities."""
        self.registered_agents[role] = capabilities
        logger.info(f"Registered agent role: {role} with capabilities: {capabilities}")

    def route_task(self, task_description: str) -> str:
        """Route a task to the appropriate agent using the LLM bridge."""
        if not self.registered_agents:
            logger.warning("No agents registered for task routing.")
            return "No agents available"

        # Construct prompt for the LLM
        prompt = (
            f"Given the task: '{task_description}', "
            f"which agent is best suited? Available agents: {list(self.registered_agents.keys())}"
        )

        try:
            # Query LLM to decide
            response = self.llm_bridge.generate_response(prompt)
            # Simple parsing: find the first matching agent name in response
            for agent in self.registered_agents:
                if agent.lower() in response.lower():
                    logger.info(f"Routed task to agent: {agent}")
                    return str(agent)

            # Default to first if LLM response is ambiguous
            default_agent = list(self.registered_agents.keys())[0]
            logger.info(f"Ambiguous LLM response. Defaulting routing to: {default_agent}")
            return str(default_agent)
        except Exception as e:
            logger.error(f"Error during task routing via LLM: {e}")
            return "Error routing task"

    def execute_task(self, role: str, task_description: str) -> Dict[str, Any]:
        """Execute a task via a specific agent."""
        if role not in self.registered_agents:
            raise ValueError(f"Unknown agent role: {role}")

        # Parse task_id from description if possible, otherwise hash
        match = re.search(r"TASK:\s+([a-zA-Z0-9-]+)", task_description)
        if match:
            task_id = match.group(1)
        else:
            task_id = hashlib.md5(task_description.encode()).hexdigest()[:8]

        logger.info(f"Executing task via agent {role}: {task_description}")

        # Simulate execution with occasional failure
        status = "failed" if random.random() < 0.1 else "success"

        # Circuit breaker check via observer
        allowed = self.task_observer.record_task_attempt(task_id, status)

        if not allowed:
            logger.warning(f"Task {task_id} execution blocked by circuit breaker.")
            self.task_observer.update_status_dashboard()
            return {
                "status": "blocked",
                "agent": role,
                "task": task_description,
                "result": "Circuit breaker tripped",
            }

        self.task_observer.update_status_dashboard()

        return {
            "status": status,
            "agent": role,
            "task": task_description,
            "result": "Mock result",
        }
