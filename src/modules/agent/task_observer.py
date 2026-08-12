import logging
import os
import re
from typing import Dict

logger = logging.getLogger(__name__)


class TaskObserver:
    """
    Skill to monitor agent progress, manage circuit breakers, and maintain project metrics.
    """

    MAX_RETRIES_PER_TASK = 3

    def __init__(self, backlog_path: str = "docs/backlog.md", status_path: str = "docs/status.md"):
        self.backlog_path = backlog_path
        self.status_path = status_path
        # task_id -> failure_count
        self.task_failures: Dict[str, int] = {}

    def record_task_attempt(self, task_id: str, status: str) -> bool:
        """
        Record the attempt of a task.
        If status is 'failed', increments failure count.
        Returns False if the task has tripped the circuit breaker, True otherwise.
        """
        if status == "success":
            self.task_failures[task_id] = 0
            return True
        elif status == "failed":
            self.task_failures[task_id] = self.task_failures.get(task_id, 0) + 1
            if self.task_failures[task_id] >= self.MAX_RETRIES_PER_TASK:
                logger.error(f"Circuit breaker tripped for task {task_id}. Marking as BLOCKED.")
                self._mark_task_blocked(task_id)
                return False
            return True
        return True

    def _mark_task_blocked(self, task_id: str) -> None:
        """
        Updates the backlog.md to mark a task as BLOCKED.
        """
        if not os.path.exists(self.backlog_path):
            return

        try:
            with open(self.backlog_path, "r") as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if task_id in line and "- [" in line:
                    lines[i] = line.replace("- [ ]", "- [BLOCKED]").replace("- [x]", "- [BLOCKED]")

            with open(self.backlog_path, "w") as f:
                f.writelines(lines)
        except Exception as e:
            logger.error(f"Failed to mark task {task_id} as blocked: {e}")

    def update_status_dashboard(self) -> None:
        """
        Recalculates completion metrics by parsing backlog.md and updates status.md.
        """
        if not os.path.exists(self.backlog_path) or not os.path.exists(self.status_path):
            return

        total_tasks = 0
        completed_tasks = 0
        pending_tasks = 0
        blocked_tasks = 0

        try:
            with open(self.backlog_path, "r") as f:
                lines = f.readlines()

            for line in lines:
                # Basic match for tasks, assuming format: - [ ] TASK: or - [x] TASK: or - [BLOCKED] TASK:
                if re.match(r"^\s*-\s+\[.*?\]", line):
                    # Exclude headers or things that aren't actually tasks if needed, but normally tasks start with - [ ]
                    if (
                        "TASK:" in line
                        or "CLEANUP:" in line
                        or "VERIFY:" in line
                        or "AUDIT:" in line
                    ):
                        total_tasks += 1
                        if "- [x]" in line or "- [DONE]" in line:
                            completed_tasks += 1
                        elif "- [BLOCKED]" in line:
                            blocked_tasks += 1
                        else:
                            pending_tasks += 1

            completion_percentage = (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            )

            with open(self.status_path, "r") as f:
                status_content = f.read()

            # Update the metrics section
            metrics = (
                f"- **Total Backlog Items:** {total_tasks}\n"
                f"- **Completed Items:** {completed_tasks}\n"
                f"- **Pending Items:** {pending_tasks}\n"
                f"- **Blocked Items:** {blocked_tasks}\n"
                f"- **Completion Percentage:** {completion_percentage:.2f}%"
            )

            status_content = re.sub(
                r"- \*\*Total Backlog Items:\*\*.*?- \*\*Completion Percentage:\*\* [0-9.]+%",
                metrics,
                status_content,
                flags=re.DOTALL,
            )

            with open(self.status_path, "w") as f:
                f.write(status_content)

        except Exception as e:
            logger.error(f"Failed to update status dashboard: {e}")
