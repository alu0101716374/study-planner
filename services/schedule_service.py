from lib.state_manager import get_repository
from typing import Tuple
from lib.auth import get_user
from lib.ui import handle_result
from services.scheduler import generate_schedule
from lib.logger import logger




def load_schedule(user_id) -> Tuple[bool, dict | str]:
    try:
        repository = get_repository()
        user = handle_result(get_user())
        tasks = repository.get_tasks_for_user(user.id)
        availability = repository.get_user_availability(user.id)
        schedule = generate_schedule(tasks, availability)
        if schedule:
            return True, schedule
        else:
            return False, "No schedule found for this user."
    except Exception as e:
        logger.error(f"Error loading schedule for user {user_id}: {e}")
        return False, f"Error accessing repository: {e}"