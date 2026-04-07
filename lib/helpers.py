from lib.supabase_client import supabase
import streamlit as st

def get_tasks():
    try:
        user = supabase.auth.get_user()
        
        if not user or not user.user:
            return []

        user_id = user.user.id

        response = supabase.table("Tasks") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("deadline") \
            .execute()

        return response.data

    except Exception as e:
        st.error(f"Error fetching tasks: {e}")
        return []
    
def complete_session():
  pass