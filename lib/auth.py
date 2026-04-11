import streamlit as st
from lib.supabase_client import supabase
from lib.repository import StudyPlannerRepository
from lib.logger import logger
from typing import Tuple, Union, Optional, Any


def init_session():
    """
    initializes all necessasy st.session_states
    """
    if "user" not in st.session_state:
        st.session_state.user = None
    if "profile" not in st.session_state:
        st.session_state.profile = None
    if "repository" not in st.session_state:
        st.session_state.repository = StudyPlannerRepository(supabase_client=supabase)


def get_user() -> tuple[bool, Optional[Any]]:
    """
    Returns a bool of succes and current user(dict including id, email), or None if not logged in
    """
    user = st.session_state.get("user")
    return user is not None, user


def get_profile() -> Tuple[bool, Union[dict, str]]:
    """
    Retrieves user profile from the profiles table.
    Caches the result in session_state.
    """
    if st.session_state.profile:
        return True, st.session_state.profile

    if st.session_state.user:
        try:
            res = (
                supabase.table("profiles")  # type: ignore
                .select("*")
                .eq("id", st.session_state.user.id)  # type: ignore
                .single()
                .execute()
            )
            st.session_state.profile = res.data
            return True, res.data
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            return False, f"Error fetching profile: {e}"
    return False, "User not found"


def sync_session_state(session=None):
    """
    Syncs the Supabase session with Streamlit session state.
    Ensures Postgrest is authenticated and profile is loaded.
    """
    if session and session.user:
        st.session_state.supabase_session = session
        st.session_state.user = session.user
        supabase.postgrest.auth(session.access_token)
        if not st.session_state.profile:
            get_profile()
    else:
        st.session_state.user = None
        st.session_state.profile = None
        st.session_state.supabase_session = None


def handle_oauth_callback() -> Tuple[bool, str]:
    """
    Checks for OAuth code in URL, exchanges it for a session, and reruns.
    """
    code = st.query_params.get("code")
    if code:
        try:
            res = supabase.auth.exchange_code_for_session({"auth_code": code})  # type: ignore
            sync_session_state(res.session)
            st.query_params.clear()
            st.rerun()
            return True, "OAuth successful"
        except Exception as e:
            logger.error(f"OAuth exchange failed: {e}")
            st.query_params.clear()
            return False, f"OAuth exchange failed: {e}"
    return False, "No OAuth code found"


def restore_session() -> Tuple[bool, str]:
    """
    Attempts to restore session from URL or persistent storage.
    """
    try:
        success, msg = handle_oauth_callback()
        if success:
            return True, msg

        res = supabase.auth.get_session()  # type: ignore
        if res:
            sync_session_state(res)
            return True, "Session restored from storage"

    except Exception as e:
        logger.error(f"Session restoration failed: {e}")
        return False, f"Session restoration failed: {e}"
    return False, "No session to restore"


def sign_in(email: str, password: str) -> Tuple[bool, str]:
    """
    Attempts to sign user in with email and password, returns whether it was a success,and an error string
    """
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})  # type: ignore
        if res.user:
            sync_session_state(res.session)
            return True, "Sign in successful"
        return False, "Sign in failed"
    except Exception as e:
        logger.error(f"Error during sign-in: {e}")
        return False, "Error during sign-in: " + str(e)


def sign_up(email: str, password: str, username: str) -> Tuple[bool, str]:
    """
    Attempts to sign up a user, in case of failiure, returns False and the error in string format
    """
    try:
        res = supabase.auth.sign_up(  # type: ignore
            {"email": email, "password": password, "options": {"data": {"full_name": username}}}
        )
        if res.user:
            st.session_state.supabase_session = res.session
            st.session_state.user = res.user

        if res.session:
            supabase.postgrest.auth(res.session.access_token)  # type: ignore
        return True, "Sign up successful"
    except Exception as e:
        logger.error(f"Error during sign-up: {e}")
        return False, "Error during sign-up: " + str(e)


def sign_in_with_google() -> None:
    """
    signs in using supabase oauth google
    """
    res = supabase.auth.sign_in_with_oauth({"provider": "google"})  # type: ignore
    st.markdown(f'<meta http-equiv="refresh" content="0; url={res.url}">', unsafe_allow_html=True)  # type: ignore


def logout() -> None:
    """
    unauthenticates user from supabase and resets session states
    """
    supabase.auth.sign_out()  # type: ignore
    st.session_state.user = None
    st.session_state.profile = None
    st.rerun()
