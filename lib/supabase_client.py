import streamlit as st
from supabase import create_client

@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["connections"]["supabase"]["SUPABASE_URL"],
        st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
    )

supabase = get_supabase()