import streamlit as st
from lib.ui import render_sidebar, handle_result
from lib.auth import get_user
from services.task_service import TaskService

# Instantiate service with repository
task_service = TaskService(st.session_state.repository)


def add_task_ui():
    title = st.text_input("Title", key="task_title_input")
    subject = st.text_input("Subject", key="task_subject_input")
    hours = st.number_input("Hours needed", key="task_hours_input")
    deadline = st.date_input("Deadline", key="tasks_deadline_input")
    difficulty = st.slider("Difficulty from 1 to 5", min_value=1, max_value=5)
    description = st.text_area("Description (optional)", key="tasks_description_input")
    user = handle_result(get_user())
    task_data = {
        "user_id": user.id,
        "task": title,
        "hours": hours,
        "deadline": str(deadline),
        "completed": 0,
        "description": description,
        "subject": subject,
        "difficulty": difficulty,
    }
    if st.button("Add Task", key="add_task_btn"):
        handle_result(
            task_service.add_task(task_data, st.session_state.repository), display_success=True
        )


def main():
    render_sidebar()

    st.title("Add a task")
    add_task_ui()


if __name__ == "__main__":
    main()
