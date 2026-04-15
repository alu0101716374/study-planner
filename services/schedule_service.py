from typing import Tuple 
from lib.auth import get_user
from lib.ui import handle_result
from services.scheduler import generate_schedule
from lib.logger import logger
from lib.repository import StudyPlannerRepository


def load_schedule(repository: StudyPlannerRepository) -> Tuple[bool, dict | str]:
    try:
        repository 
        user = handle_result(get_user())
        if user is None:
            logger.error("User not authenticated or user object is invalid.")
            return False, "User not authenticated."

        tasks = repository.get_tasks_for_user(user.id)
        availability = repository.get_user_availability(user.id)
        schedule = generate_schedule(tasks, availability)
        if schedule:
            return True, schedule
        else:
            return False, "No schedule found for this user."
    except Exception as e:
        logger.error(f"Error loading schedule for user {user.id if user else 'unknown'}: {e}")
        return False, f"Error accessing repository: {e}"
