import streamlit as st
from lib.auth import get_user, logout, get_profile
from app import show_pages

def render_sidebar():

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