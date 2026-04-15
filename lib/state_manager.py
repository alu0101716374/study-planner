import streamlit as st
from lib.repository import StudyPlannerRepository
from services.schedule_service import load_schedule
from services.task_service import TaskService 
from typing import Tuple
from lib.logger import logger


def get_repository() -> StudyPlannerRepository:
    return st.session_state["repository"]

def get_task_service() -> TaskService:
    if "task_service" not in st.session_state:
        st.session_state["task_service"] = TaskService(get_repository())
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
