import streamlit as st
from lib.auth import logout, get_profile
from lib.ui import render_sidebar, handle_result

profile = handle_result(get_profile())

@st.dialog("⚠️ Delete Account Forever")
def confirm_delete_dialog():
    st.write(f"""
        {profile['display_name']}, are you sure you want to delete your Study Planner account? 
        This action is **permanent** and will:
    """)
    st.markdown("- Delete all data associated to the account")
    
    st.warning("This cannot be undone.", icon="🚨")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun() 
            
    with col2:
        if st.button("Delete Forever", type="primary", use_container_width=True):
            st.session_state.repository.delete_self()
            st.success("Account deleted.")
            logout()



def main():
    render_sidebar()
    st.title("Settings")
    st.subheader("Danger Zone")

    if st.button("Delete My Account", type="secondary"):
        confirm_delete_dialog()

if __name__ == "__main__":
    main()