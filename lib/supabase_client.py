import streamlit as st
from supabase import create_client
from typing import Optional, Any


def get_supabase() -> Optional[Any]:
    return create_client(
        st.secrets["connections"]["supabase"]["SUPABASE_URL"],
        st.secrets["connections"]["supabase"]["SUPABASE_KEY"],
    )


supabase = get_supabase()
