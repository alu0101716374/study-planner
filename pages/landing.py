import streamlit as st
from lib.auth import get_user
from lib.ui import handle_result, render_sidebar


def main():
    render_sidebar()
    st.title("AI Study Planner")

    user = handle_result(get_user())

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### What it does:
        - Upload daily tasks
        - Smart reordering
        - AI plans
        """)
        if st.button("Try Now", type="primary"):
            if user:
                st.switch_page("pages/dashboard.py")
            else:
                st.switch_page("pages/login.py")


if __name__ == "__main__":
    main()
