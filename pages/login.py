import streamlit as st
from lib.auth import get_user, sign_in, sign_in_with_google, sign_up
from lib.ui import render_sidebar, handle_result


def sign_up_ui():
    """
    shows ui for signing up and handles manual user sign up
    """
    email = st.text_input(label="Email", key="SignUpEmailInput")
    username = st.text_input(label="Display Name", key="SignUpUsernameInput")
    password = st.text_input(label="Password", type="password", key="SignUpPasswordInput")

    if st.button("Sign Up"):
        handle_result(sign_up(email, password, username), display_success=True)


def sign_in_ui():
    """
    shows ui for user sign in and handles manual sign in
    """
    email = st.text_input(label="Email", key="LogInEmailInput")
    password = st.text_input(label="Password", type="password", key="LogInPasswordInput")

    if st.button("Sign In"):
        handle_result(sign_in(email, password), display_success=True)


def main():
    render_sidebar()
    st.title("Login")

    user = handle_result(get_user())

    if not user:
        if st.button("Continue with Google"):
            sign_in_with_google()

        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            sign_in_ui()
        with tab2:
            sign_up_ui()
        st.caption("If you signed up with Google, use Google login")
    else:
        st.success("Already logged in")


if __name__ == "__main__":
    main()
