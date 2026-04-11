import streamlit as st
from lib.auth import get_profile
from lib.ui import render_sidebar, handle_result


def main():
    render_sidebar()
    profile = handle_result(get_profile())
    st.write(f"name: {profile['display_name']}, Plan: {profile['plan']}")


if __name__ == "__main__":
    main()
