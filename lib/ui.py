import streamlit as st
from lib.auth import logout, get_profile, get_user
from typing import Optional, Any, Tuple, TYPE_CHECKING
from lib.state_manager import get_repository, reset_profile_cache

if TYPE_CHECKING:
    from lib.models import StudySession


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
    settings_page = st.Page("pages/settings.py", title="Settings")

    user = handle_result(get_user())

    st.set_page_config(
        page_title="Smart Study Planner", layout="wide", initial_sidebar_state="expanded"
    )

    if user:
        pages = [dashboard_page, schedule_page, tasks_page, availability_page, settings_page]

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


def handle_done_click(session: "StudySession"):
    repo = get_repository()
    profile = get_profile()

    try:
        if session.id is None:
            new_id = repo.persist_single_session_and_get_id(profile["id"], session)
            session.id = new_id

        success = repo.complete_session(session.id, session.task_id, session.hours)

        if success:
            reset_profile_cache()
            st.success(f"Nice work on {session.subject}!")
            st.rerun()

    except Exception as e:
        st.error(f"Could not complete session: {e}")


def render_session(session: "StudySession"):
    unique_key = session.id if session.id else f"draft_{session.task_id}_{session.hours}"
    load_labels = ["Very Low", "Low", "Medium", "High", "Critical"]
    load_label = load_labels[session.difficulty - 1] if 1 <= session.difficulty <= 5 else "Medium"

    with st.container(border=True):
        st.markdown('<span class="session-card-trigger"></span>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([1, 3, 2, 1])

        with c1:
            st.markdown(
                f"<h2 style='margin:0; color:var(--primary);'>{session.hours}h</h2>",
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(f"**{session.title}**")
            st.caption(session.subject)

        with c3:
            st.markdown(
                f'<span class="load-badge diff-{session.difficulty}">LOAD: {load_label}</span>',
                unsafe_allow_html=True,
            )

        with c4:
            if session.is_completed:
                st.write("✅")
            else:
                if st.button("DONE", key=f"btn_{unique_key}", use_container_width=True):
                    handle_session_completion(get_repository(), session)

        if session.description:
            with st.expander("View Details"):
                st.write(session.description)


def handle_session_completion(repo, session):
    _, user = get_user()

    if session.id is None:
        new_id = repo.persist_single_session_and_get_id(user.id, session)
        session.id = new_id

    success = repo.complete_session(session.id, session.task_id, session.hours)
    if success:
        from lib.state_manager import reset_profile_cache

        reset_profile_cache()
        st.rerun()
