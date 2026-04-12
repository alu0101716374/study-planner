import streamlit as st
from typing import Dict

def get_repository() -> Dict:
    return st.session_state['repository']