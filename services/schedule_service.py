from typing import Tuple, Dict, TYPE_CHECKING
from lib.auth import get_user
from services.scheduler import generate_schedule
from lib.logger import logger
from datetime import datetime
import streamlit as st

if TYPE_CHECKING:
    from lib.repository import StudyPlannerRepository


def load_schedule(repository: "StudyPlannerRepository") -> Tuple[bool, dict | str]:
    success, user = get_user()
    if not success:
        st.error("User not logged in")
    try:
        if user is None:
            logger.error("User not authenticated or user object is invalid.")
            return False, "User not authenticated."

        tasks = repository.get_tasks_for_user(user.id)
        availability = repository.get_user_availability(user.id)
        existing_scheduled_sessions = repository.get_user_scheduled_sessions(user.id)
        schedule = generate_schedule(tasks, availability, existing_scheduled_sessions)
        print(schedule)
        if schedule:
            repository.persist_schedule(user.id, schedule)
            return True, schedule
        else:
            return False, "No schedule found for this user."
    except Exception as e:
        logger.error(f"Error loading schedule for user {user.id if user else 'unknown'}: {e}")
        return False, f"Error accessing repository: {e}"


def get_daily_stats(repository: "StudyPlannerRepository") -> Dict:
    """
    Calculates today's study metrics by querying persistent schedule items.
    Returns a dictionary for easy UI mapping.
    """
    success, user = get_user()
    if not success:
        st.error("User not logged in")
    try:
        sessions = repository.get_todays_sessions(user.id)
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s["is_completed"]])

        total_hours = sum(s["hours_allocated"] for s in sessions)
        completed_hours = sum(s["hours_allocated"] for s in sessions if s["is_completed"])

        progress_percentage = (completed_hours / total_hours) if total_hours > 0 else 0.0

        return {
            "date": datetime.now().date().isoformat(),
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "remaining_sessions": total_sessions - completed_sessions,
            "total_hours": round(total_hours, 2),
            "completed_hours": round(completed_hours, 2),
            "progress_percentage": round(progress_percentage, 2),
            "is_day_complete": (
                (completed_sessions == total_sessions) if total_sessions > 0 else False
            ),
        }

    except Exception as e:
        logger.error(f"Error calculating daily stats: {e}")
        return {"total_sessions": 0, "completed_hours": 0, "progress_percentage": 0, "error": True}
