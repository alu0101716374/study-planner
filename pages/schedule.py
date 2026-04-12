import streamlit as st
from lib.ui import render_sidebar, handle_result
from lib.auth import get_user
from services.schedule_service import load_schedule

def display_schedule():
    st.title("Your Schedule")

    user = handle_result(get_user())
    schedule = handle_result(load_schedule(user.id))

    if not schedule:
        st.info("No schedule available. Please add some tasks and set your availability.")
        return

    # Create tabs for each day
    days = list(schedule.keys())
    tabs = st.tabs(days)

    for i, day in enumerate(days):
        with tabs[i]:
            sessions = schedule[day]

            if not sessions:
                st.info("No sessions for this day.")
                continue

            for session in sessions:
                with st.container():
                    st.markdown(f"###  {session.subject}")
                    st.write(f"**Hours needed:** {session.hours}")
                    st.write(f"**Deadline:** {session.deadline}")
                    st.write(f"**Difficulty:** {session.difficulty}")
                    st.divider()
def main():
        render_sidebar()
        display_schedule()

if __name__ == "__main__":
    main()