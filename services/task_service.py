from lib.models import Task
from lib.repository import StudyPlannerRepository  # type: ignore
from lib.logger import logger
from typing import Tuple


class TaskService:
    def __init__(self, repository: StudyPlannerRepository):
        self.repository = repository

    def add_task(self, task_data: dict, repository: StudyPlannerRepository) -> Tuple[bool, str]:
        """Add a task with validation and error handling. Returns (success, message)."""
        try:
            # Business logic: Validate input
            if not task_data.get("task") or task_data.get("hours", 0) <= 0:
                return False, "Title is required and hours must be positive."

            task = Task.from_dict(task_data)
            self.repository.add_task(task)
            logger.info(f"Task added: {task.title}")
            return True, "Task added successfully."
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return False, f"Invalid task data: {e}"
        except Exception as e:
            logger.error(f"Unexpected error adding task: {e}")
            return False, "An unexpected error occurred. Please try again."
