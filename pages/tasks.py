import streamlit as st
from lib.ui import render_sidebar
from lib.auth import get_user
from lib.supabase_client import supabase

def AddTask():
  title = st.text_input("Title", key="task_title_input")
  subject = st.text_input("Subject", key="task_subject_input")
  hours = st.number_input("Hours needed", key="task_hours_input")
  deadline = st.date_input("Deadline", key="tasks_deadline_input")
  difficulty = st.slider("Difficulty from 1 to 5", min_value=1, max_value=5)
  description = st.text_area("Description (optional)", key="tasks_description_input")
  if st.button("Add Task", key="add_task_btn"):
    if "supabase_session" in st.session_state:
      required_fields = [title, subject, hours, deadline, difficulty]
      
      if all(required_fields):
          user = get_user()
          token = st.session_state.supabase_session.access_token
          supabase.postgrest.auth(token)
          try:
            task = {
              "user_id": user.id,
              "task": title,
              "hours": hours,
              "deadline": str(deadline), 
              "completed": 0,
              "description": description,
              "subject": subject,
              "difficulty": difficulty
          }
            supabase.table("Tasks").insert(task).execute()
            st.success("Task added successfully!")
          except Exception as e:
              st.error(f"RLS or Database Error: {e}")
      else:
          st.error("Please fill out all necessary fields (Title, Subject, Hours, Deadline, and Difficulty).")
    else:
       st.error("Session Error")

def main(): 
  render_sidebar()

  st.title("Add a task")
  AddTask()

if __name__ == "__main__":
  main()