import streamlit as st
from lib.auth import logout, get_profile, get_user
from typing import Optional, Any, Tuple


def handle_result(call_result: Tuple[bool, Any], display_success: bool = False) -> Optional[Any]:
    """
    Helper to handle function results that return (bool, data_or_message).
    Displays messages via st.success/st.error() and returns data on success, None/False on failure.

    Args:
        call_result: Tuple like (success: bool, data: Any or message: str)
        display_success: If True, displays success message with st.success() and returns True.
                         If False, returns data on success, None on failure.

    Returns:
        - If display_success=True: True on success (message displayed), False on failure (error displayed).
        - If display_success=False: Data on success, None on failure (error displayed).
    """
    success, data = call_result
    if success:
        if display_success:
            st.success(data)
            return True
        else:
            return data
    else:
        if display_success:
            st.error(data)
        return None if not display_success else False


def render_sidebar():
    """
    Renders the sidebar with user profile information and navigation options.
    """
    with st.sidebar:
        profile = handle_result(get_profile(), display_success=False)
        if profile:
            st.title(f"📚 {profile['display_name']}'s  Planner")
            st.divider()

            if st.button("Logout"):
                logout()
                show_pages()

        else:
            st.info("Not logged in")


def show_pages():
    """
    Defines the pages and navigation logic based on user authentication status.
    """
    landing_page = st.Page("pages/landing.py", title="Study Planner")
    login_page = st.Page("pages/login.py", title="Log In / Sign Up")
    dashboard_page = st.Page("pages/dashboard.py", title="Dashboard")
    tasks_page = st.Page("pages/tasks.py", title="Tasks")
    availability_page = st.Page("pages/availability.py", title="Availability")
    schedule_page = st.Page("pages/schedule.py", title="Schedule")

    user = handle_result(get_user())
    
    st.set_page_config(page_title="Smart Study Planner", layout="wide", initial_sidebar_state="expanded")

    if user:
        pages = [dashboard_page, schedule_page, tasks_page, availability_page]

    else:
        pages = [landing_page, login_page]

    pg = st.navigation(pages)
    pg.run()


def load_css():
    """
    Loads a CSS file from the static/css directory and injects it into the Streamlit app.
    """
    with open("static/css/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
