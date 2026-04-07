import streamlit as st
from lib.auth import init_session, restore_session, get_user
from lib.repository import StudyPlannerRepository
from lib.supabase_client import supabase

def show_pages():
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

def main():
    init_session()
    restore_session()
    show_pages()
    if "repository" not in st.session_state:
        st.session_state.repository = StudyPlannerRepository(supabase_client=supabase)

if __name__ == "__main__":
   main()