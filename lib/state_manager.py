import streamlit as st
from services.schedule_service import load_schedule
from typing import Tuple, TYPE_CHECKING
from lib.logger import logger
from lib.repository import StudyPlannerRepository
from lib.supabase_client import supabase
from lib.repository import StudyPlannerRepository
if TYPE_CHECKING:
    from services.task_service import TaskService



def init_session():
    """
    initializes all necessasy st.session_states
    """
    if "user" not in st.session_state:
        st.session_state.user = None
    if "profile" not in st.session_state:
        st.session_state.profile = None
    if "repository" not in st.session_state:
        st.session_state.repository = StudyPlannerRepository(supabase_client=supabase)
    if "schedule" not in st.session_state:
        st.session_state.schedule = None

def get_repository() -> StudyPlannerRepository:
    return st.session_state["repository"]

def get_task_service() -> "TaskService":
    if "task_service" not in st.session_state:
        st.session_state["task_service"] = "TaskService"(get_repository())
    return st.session_state["task_service"]

def update_schedule() -> Tuple[bool, dict | str]:
    logger.info("Updating schedule")
    success, data = load_schedule(get_repository())
    st.session_state["schedule"] = (success, data)
    return success, data

def get_schedule() -> Tuple[bool, dict | str]:
    if "schedule" not in st.session_state or st.session_state["schedule"] is None:
        return update_schedule()
    return st.session_state["schedule"]

def reset_profile_cache():
    st.session_state.profile = None