import streamlit as st
from lib.supabase_client import supabase
from lib.repository import StudyPlannerRepository
from lib.logger import logger

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
    
def get_user():
    """
        Returns the current user, which includes:
            id, email
    """
    return st.session_state.get("user")

def get_profile():
    """
    Retrieves user profile from the profiles table.
    Caches the result in session_state.
    """
    if st.session_state.profile:
        return st.session_state.profile

    if st.session_state.user:
        try:
            res = supabase.table("profiles") \
                .select("*") \
                .eq("id", st.session_state.user.id) \
                .single() \
                .execute()
            st.session_state.profile = res.data
            return res.data
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")    
            st.error(f"Error fetching profile: {e}")
    return None

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

def handle_oauth_callback() -> bool:
    """
    Checks for OAuth code in URL, exchanges it for a session, and reruns.
    """
    code = st.query_params.get("code")
    if code:
        try:
            res = supabase.auth.exchange_code_for_session({"auth_code": code})
            sync_session_state(res.session)
            st.query_params.clear()
            st.rerun()
            return True
        except Exception as e:
            logger.error(f"OAuth exchange failed: {e}")
            st.error(f"OAuth exchange failed: {e}")
            st.query_params.clear()
    return False

def restore_session():
    """
    Attempts to restore session from URL or persistent storage.
    """
    try:
        if handle_oauth_callback():
            return

        res = supabase.auth.get_session()
        if res:
            sync_session_state(res)
            
    except Exception as e:
        logger.error(f"DEBUG: Session restoration skipped or failed: {e}")

def sign_in(email, password) -> bool:
    """
        Attempts to sign user in with email and password, returns whether it was a success,and an error string
    """
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            sync_session_state(res.session)
            return True, None
    except Exception as e:
        logger.error(f"Error during sign-in: {e}")
        return False, str(e)
    
def sign_up(email, password, username):
    """
        Attempts to sign up a user, in case of failiure, returns False and the error in string format
    """
    try:
        res = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"full_name": username}
                }
            })
        if res.user:
            st.session_state.supabase_session = res.session
            st.session_state.user = res.user
                
        if res.session:
            supabase.postgrest.auth(res.session.access_token)
        return True, None
    except Exception as e:
        logger.error(f"Error during sign-up: {e}")
        return False, str(e)
            

def sign_in_with_google():
    """
        signs in using supabase oauth google
    """
    res = supabase.auth.sign_in_with_oauth({"provider": "google"})
    st.markdown(
        f'<meta http-equiv="refresh" content="0; url={res.url}">',
        unsafe_allow_html=True
    )

def logout():
    """
        unauthenticates user from supabase and resets session states
    """
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.profile = None
    st.rerun()