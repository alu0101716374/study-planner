from lib.models import Task
from lib.repository import StudyPlannerRepository  # type: ignore
from lib.logger import logger
from typing import Tuple, Optional


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

    def mark_session_complete(self, task_id: int, session_hours: float) -> Tuple[bool, str]:
        try:
            task = self.repository.get_task_by_id(task_id)
            if task is None:
                return False, f"Task with ID {task_id} not found."

            task.mark_session_complete(session_hours)
            updated_task = self.repository.update_task(task)

            if updated_task is None:
                return False, f"Failed to update task {task_id} in the repository."

            return True, f"Task '{task.title}' updated to {task.completed_percent}% complete."
        except Exception as e:
            logger.error(f"Error marking session complete for task {task_id}: {e}")
            return False, f"Error marking session complete: {e}"
