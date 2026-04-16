import streamlit as st
from datetime import datetime
from lib.ui import render_sidebar
from lib.state_manager import get_schedule, get_repository, reset_profile_cache

WEEKDAYS = [
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday"
]

def render_session(session, session_id):
    # 'session' here is now a dictionary from the DB join
    # 'session_id' is the ID from the schedule_items table
    
    task_info = session.get('tasks', {})
    is_done = session.get('is_completed', False)
    hours = session.get('hours_allocated', 0)
    task_id = session.get('task_id')
    
    difficulty_icons = "🔹" * task_info.get('difficulty', 3)

    with st.container():
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>{task_info.get('task', 'Unknown Task')}</h4>
                <p><b>📘 Subject:</b> {task_info.get('subject', 'N/A')}</p>
                <p><b>⏱ Planned:</b> {hours}h</p>
                <p><b>⚡ Difficulty:</b> {difficulty_icons}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if is_done:
            st.success("✅ This session is complete!")
        else:
            if st.button(f"Mark as Complete", key=f"sched_complete_{session_id}"):
                repo = get_repository()
                success = repo.complete_session(session_id, task_id, hours)
                if success:
                    reset_profile_cache() 
                    st.rerun()

def display_schedule():
    st.title("📅 Your Schedule")
    repo = get_repository()
    
    success, schedule_data = get_schedule() 

    if not success:
        st.info("No schedule available. Try generating one in the tasks section.")
        return

    today_index = datetime.today().weekday()
    ordered_days = WEEKDAYS[today_index:] + WEEKDAYS[:today_index]
    tabs = st.tabs([day.capitalize() for day in ordered_days])

    for i, day in enumerate(ordered_days):
        with tabs[i]:
            sessions = schedule_data.get(day, [])

            if not sessions:
                st.write("✨ No study sessions planned for this day.")
                continue

            for s in sessions:
                render_session(s, getattr(s, 'id', None))

def main():
    render_sidebar()
    display_schedule()

if __name__ == "__main__":
    main()