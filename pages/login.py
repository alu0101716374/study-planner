import streamlit as st
from lib.supabase_client import supabase
from lib.auth import get_user, init_session, restore_session
from lib.ui import render_sidebar
from app import show_pages


def SignUp():
    email = st.text_input("Email", key="SignUpEmailInput")
    username = st.text_input("Display Name", key="SignUpUsernameInput")
    password = st.text_input("Password", type="password", key="SignUpPasswordInput")

    if st.button("Sign Up"):
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"full_name": username}
            }
        })

        if res.user:
            st.success("Account created!")
            st.session_state.supabase_session = res.session
            st.session_state.user = res.user
            
            if res.session:
                supabase.postgrest.auth(res.session.access_token)
            
            st.rerun()


def LogIn():
    email = st.text_input("Email", key="LogInEmailInput")
    password = st.text_input("Password", type="password", key="LogInPasswordInput")

    if st.button("Sign In"):
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if res.user:
            st.session_state.supabase_session = res.session 
            st.session_state.user = res.user
            
            supabase.postgrest.auth(res.session.access_token)
            
            st.rerun()

def main():
    render_sidebar()
    init_session()
    restore_session() 
    st.title("Login")

    user = get_user()

    if not user:
        if st.button("Continue with Google"):
            res = supabase.auth.sign_in_with_oauth({"provider": "google"})
            st.markdown(
                f'<meta http-equiv="refresh" content="0; url={res.url}">',
                unsafe_allow_html=True
            )

        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            LogIn()
        with tab2:
            SignUp()
        st.caption("If you signed up with Google, use Google login")
    else:
        st.success("Already logged in")

if __name__ == "__main__":
    main()
