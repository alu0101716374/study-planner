import streamlit as st
from lib.supabase_client import supabase

def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None
def restore_session():
    params = st.query_params
    
    if "code" in params:
        auth_code = params["code"]
        if isinstance(auth_code, list):
            auth_code = auth_code[0]
            
        try:
            res = supabase.auth.exchange_code_for_session({"auth_code": auth_code})
            if res.user:
                st.session_state.supabase_session = res.session
                st.session_state.user = res.user
                
                supabase.postgrest.auth(res.session.access_token)
                
                st.query_params.clear()
                st.rerun()
        except Exception as e:
            st.error(f"Failed to exchange code: {e}")

    try:
        res = supabase.auth.get_session()
        if res and res.session:
            st.session_state.supabase_session = res.session
            st.session_state.user = res.session.user
            
            supabase.postgrest.auth(res.session.access_token)
        else:
            st.session_state.user = None
            st.session_state.supabase_session = None
    except Exception:
        pass
    
def get_user():
    return st.session_state.get("user")

def get_profile():
    user = get_user()
    if user:
        profile = supabase.table("profiles") \
        .select("*") \
        .eq("id", user.id) \
        .single() \
        .execute().data
        return profile
    else: return None


def require_auth():
    user = get_user()
    if not user:
        st.switch_page("pages/login.py")
        st.stop()
    return user

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()