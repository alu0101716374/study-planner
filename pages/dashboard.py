import streamlit as st
from lib.auth import get_profile
from lib.supabase_client import supabase
from lib.ui import render_sidebar

def main():
  render_sidebar()
  profile = get_profile()
  st.write(f"name: {profile['display_name']}, Plan: {profile['plan']}")


if __name__ == "__main__":
    main()