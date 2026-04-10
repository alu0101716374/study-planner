import streamlit as st
from lib.auth import logout, get_profile, get_user

def render_sidebar():
    """   
        Renders the sidebar with user profile information and navigation options.
    """
    with st.sidebar:
        profile = get_profile()
        if profile:
          st.title(f"📚 {profile['display_name']}'s  Planner")
          st.divider()

          if st.button("Logout"):
            logout()
            show_pages()

        else:
          st.info("Not logged in")

          if st.button("Log In / Sign Up"):
            st.switch_page("pages/login.py")

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

    user = get_user()

    if user:
        pages = [dashboard_page, schedule_page, tasks_page, availability_page]
    else:
        pages = [landing_page, login_page]

    pg = st.navigation(pages) 
    pg.run()