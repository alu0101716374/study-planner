import streamlit as st
from datetime import datetime
from lib.ui import render_sidebar, render_session
from lib.state_manager import get_schedule, get_repository

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def display_schedule():
    st.title("📅 Your Schedule")

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
                render_session(s)


def main():
    render_sidebar()
    display_schedule()


if __name__ == "__main__":
    main()
