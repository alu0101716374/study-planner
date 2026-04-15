import streamlit as st
from datetime import datetime
from lib.ui import render_sidebar, handle_result
from lib.state_manager import get_schedule, get_task_service 

WEEKDAYS = [
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday"
]

def format_date(date_obj):
    return date_obj.strftime("%d %b %Y")

def render_session(session):
    progress = int(session.completed_percent)
    task_service = get_task_service() # Get the task service

    difficulty_icons = "🔹" * session.difficulty

    with st.container():
        st.markdown(
            f"""
            <div style="
                padding: 12px;
                border-radius: 10px;
                border: 1px solid #ddd;
                margin-bottom: 10px;
            ">
                <h4 style="margin-bottom: 5px;">{session.title}</h4>
                <p style="margin: 0;"><b>📘 Subject:</b> {session.subject}</p>
                <p style="margin: 0;"><b>⏱ Hours:</b> {session.hours}</p>
                <p style="margin: 0;"><b>📅 Deadline:</b> {session.deadline}</p>
                <p style="margin: 0;"><b>⚡ Difficulty:</b> {difficulty_icons}</p>
                <p style="margin: 0;"><b>ID:</b> {session.task_id}</p>
                <p style="margin: 0;"><b>📝 Description:</b> {session.description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(progress / 100)
        st.caption(f"{progress}% completed")

        if st.button(f"Mark as Complete", key=f"complete_session_{session.task_id}"):
            if session.task_id is not None:
                success, message = handle_result(task_service.mark_session_complete(session.task_id, session.hours))
                if success:
                    st.rerun()
            else:
                st.error("Cannot mark session complete: Task ID is missing.")

        st.divider()

def display_schedule():
    st.title("📅 Your Schedule")

    success, schedule = get_schedule()

    if not success:
        st.info("No schedule available.")
        return

    today_index = datetime.today().weekday()
    ordered_days = WEEKDAYS[today_index:] + WEEKDAYS[:today_index]

    tabs = st.tabs([day.capitalize() for day in ordered_days])

    for i, day in enumerate(ordered_days):
        with tabs[i]:
            sessions = schedule.get(day, [])

            if not sessions:
                st.info("No sessions for this day.")
                continue

            for session in sessions:
                render_session(session)


def main():
    render_sidebar()
    display_schedule()


if __name__ == "__main__":
    main()