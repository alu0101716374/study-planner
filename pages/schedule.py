# import streamlit as st
# from lib.supabase_client import supabase
# from services.scheduler import generate_schedule, DAYS_ORDER
# from lib.auth import get_profile
# from lib.helpers import get_tasks
# from datetime import datetime

# import time

# def start_session_timer(task_id, current_progress, total_hours):
#     # (100% / (total_hours * 60 minutes))
#     percent_per_minute = 100 / (total_hours * 60)

#     status_text = st.empty()
#     bar = st.progress(current_progress / 100)

#     if st.button("Stop Timer", key=f"stop_{task_id}"):
#         st.rerun()

#     while current_progress < 100:
#         time.sleep(60) # Wait 1 minute
#         current_progress += percent_per_minute

#         # Update Database
#         supabase.table("Tasks").update({"completed": min(100, current_progress)}).eq("id", task_id).execute()

#         # Update UI
#         status_text.write(f"Focusing... {round(current_progress, 1)}% Complete")
#         bar.progress(min(1.0, current_progress / 100))

# def mark_as_done(task_id):
#     supabase.table("Tasks").update({"completed": 100}).eq("id", task_id).execute()
#     st.success("Task Completed! 🎉")
#     st.balloons()
#     time.sleep(1)
#     st.rerun()

# def display_interactive_schedule(schedule):
#   st.header("🗓️ Your Weekly Game Plan")
#   today_index = datetime.now().weekday()
#   # Create the tabs
#   tabs = st.tabs(DAYS_ORDER)

#   for i, day in enumerate(DAYS_ORDER):
#     with tabs[i]:
#       header_text = f"### {day}"
#       if i == today_index:
#                 header_text += " (Today)"
#       sessions = schedule.get(day, [])
#       st.markdown(header_text)
#       if not sessions:
#           st.info("No sessions scheduled. Rest up!")
#       else:
#         for s in sessions:
#           # Logic to highlight if a deadline is close
#           deadline_dt = datetime.fromisoformat(s["deadline"])
#           is_due_soon = (deadline_dt.date() == datetime.now().date())

#           with st.container(border=True):
#             col1, col2 = st.columns([3, 1])

#             with col1:
#               title = f"**{s['subject']}**"
#               if is_due_soon:
#                   title += " ⚠️ (DUE TODAY)"
#               st.markdown(title)
#               st.caption(f"Duration: {s['hours']}h | Difficulty: {s['difficulty']}/5")
#               st.progress(s['completed'] / 100)

#             with col2:
#               # Unique keys are vital in Streamlit loops
#               u_key = f"{day}_{s['id']}"
#               if st.button("⏱️ Start", key=f"t_{u_key}"):
#                   # Your timer function here
#                   pass
#               if st.button("✅ Done", key=f"d_{u_key}"):
#                     mark_as_done(s['id'])


# def main():
#   tasks = get_tasks()
#   profile = get_profile()
#   availability = profile["availability"]
#   full_schedule = generate_schedule(tasks, availability)
#   display_interactive_schedule(full_schedule)

# if __name__ == "__main__":
#     main()
