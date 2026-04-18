from typing import List, Optional, Dict, Any
from datetime import date, datetime  # Added for date handling
from lib.models import Task, StudySession
from services.scheduler import get_slot_date
from lib.logger import logger


class StudyPlannerRepository:
    def __init__(self, supabase_client):
        self._supabase = supabase_client

    def get_tasks_for_user(self, user_id: str) -> List[Task]:
        try:
            res = self._supabase.table("tasks").select("*").eq("user_id", user_id).execute()
            tasks_data = res.data if res and res.data else []
            return [Task.from_dict(t_data) for t_data in tasks_data]
        except Exception as e:
            logger.error(f"Error fetching tasks for user {user_id}: {e}")
            return []

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        try:
            res = self._supabase.table("tasks").select("*").eq("id", task_id).single().execute()
            if res and res.data:
                return Task.from_dict(res.data)
            return None
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            return None

    def add_task(self, task: Task) -> Optional[Task]:
        try:
            task_dict = task.to_dict()
            res = self._supabase.table("tasks").insert(task_dict).execute()
            if res and res.data:
                return Task.from_dict(res.data[0])
            return None
        except Exception as e:
            logger.error(f"Error adding task for user {task.user_id}: {e}")
            return None

    def update_task(self, task: Task) -> Optional[Task]:
        if task.id is None:
            raise ValueError("Cannot update a task without an ID.")
        try:
            task_dict = task.to_dict()
            task_dict.pop("id", None)
            res = self._supabase.table("tasks").update(task_dict).eq("id", task.id).execute()
            if res and res.data:
                return Task.from_dict(res.data[0])
            return None
        except Exception as e:
            logger.error(f"Error updating task {task.id}: {e}")
            return None

    def delete_task(self, task_id: int) -> bool:
        try:
            res = self._supabase.table("tasks").delete().eq("id", task_id).execute()
            return len(res.data) > 0
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False

    def get_user_availability(self, user_id: str) -> Dict[str, Any]:
        try:
            res = (
                self._supabase.table("profiles")
                .select("availability")
                .eq("id", user_id)
                .single()
                .execute()
            )
            if res and res.data and "availability" in res.data:
                return res.data["availability"]
            else:
                return {}
        except Exception as e:
            logger.error(f"Error fetching availability for {user_id}: {e}")
            return {}

    def update_user_availability(self, user_id: str, availability_data: Dict[str, Any]) -> None:
        try:
            self._supabase.table("profiles").update({"availability": availability_data}).eq(
                "id", user_id
            ).execute()
        except Exception as e:
            logger.error(f"Error updating availability for {user_id}: {e}")

    def get_user_scheduled_sessions(self, user_id: str) -> Dict[date, List[StudySession]]:
        """Fetches all currently scheduled (and not completed) study sessions for a user, grouped by date."""
        scheduled_sessions: Dict[date, List[StudySession]] = {}
        try:
            res = (
                self._supabase.table("schedule_items")
                .select("*, tasks(task, subject, difficulty, deadline, completed)")
                .eq("user_id", user_id)
                .eq("is_completed", False)
                .execute()
            )

            for item_data in res.data if res and res.data else []:
                task_info = item_data.get("tasks", {})
                scheduled_date_str = item_data.get("scheduled_date")

                if scheduled_date_str:
                    scheduled_date = datetime.fromisoformat(scheduled_date_str).date()

                    session = StudySession(
                        id=item_data.get("id"),
                        task_id=item_data.get("task_id"),
                        title=task_info.get("task", "Unknown"),
                        subject=task_info.get("subject", ""),
                        hours=item_data.get("hours_allocated", 0.0),
                        difficulty=task_info.get("difficulty", 3),
                        is_completed=False,
                    )

                    if scheduled_date not in scheduled_sessions:
                        scheduled_sessions[scheduled_date] = []
                    scheduled_sessions[scheduled_date].append(session)
            return scheduled_sessions
        except Exception as e:
            logger.error(f"Error fetching scheduled sessions for {user_id}: {e}")
            return {}

    def delete_self(self) -> bool:
        try:
            logger.info("User requesting self-deletion via RPC")
            self._supabase.rpc("delete_user").execute()

            logger.info("Account wiped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete account: {e}")
            return False

    def complete_study_session(self, session_id: int, task_id: int, hours_done: float):
        self._supabase.table("schedule_items").update({"is_completed": True}).eq(
            "id", session_id
        ).execute()

        task_data = self._supabase.table("tasks").select("*").eq("id", task_id).single().execute()
        task_obj = Task.from_dict(task_data.data)

        task_obj.mark_session_complete(hours_done)

        self._supabase.table("tasks").update({"completed": task_obj.completed_percent}).eq(
            "id", task_id
        ).execute()

    def save_schedule(self, user_id: str, sessions: List[StudySession], day_name: str):
        """
        Saves a list of StudySessions for a specific day into the persistent table.
        """

        slot_date = get_slot_date(day_name).isoformat()

        all_entries = []
        for session in sessions:
            if session.task_id is None:
                continue

            all_entries.append(
                {
                    "user_id": user_id,
                    "task_id": session.task_id,
                    "scheduled_date": slot_date,
                    "hours_allocated": session.hours,
                    "is_completed": False,
                }
            )

        if all_entries:
            try:
                self._supabase.table("schedule_items").delete().eq("user_id", user_id).eq(
                    "scheduled_date", slot_date
                ).eq("is_completed", False).execute()

                self._supabase.table("schedule_items").insert(all_entries).execute()
                logger.info(f"Saved {len(all_entries)} sessions for {day_name} ({slot_date})")
            except Exception as e:
                logger.error(f"Error saving persistent schedule: {e}")

    def persist_schedule(self, user_id: str, schedule: Dict[str, List[StudySession]]):
        """Saves the generated sessions into Supabase so they are clickable."""

        all_entries = []
        for day_name, sessions in schedule.items():
            slot_date = get_slot_date(day_name).isoformat()
            for s in sessions:
                all_entries.append(
                    {
                        "user_id": user_id,
                        "task_id": s.task_id,
                        "scheduled_date": slot_date,
                        "hours_allocated": s.hours,
                        "is_completed": False,
                    }
                )

        if all_entries:
            try:
                self._supabase.table("schedule_items").delete().eq("user_id", user_id).eq(
                    "is_completed", False
                ).execute()

                self._supabase.table("schedule_items").insert(all_entries).execute()
            except Exception as e:
                logger.error(f"Failed to persist schedule: {e}")

    def get_todays_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetches today's sessions joined with Task info for the UI."""
        import datetime

        today = datetime.date.today().isoformat()
        try:
            res = (
                self._supabase.table("schedule_items")
                .select("*, tasks(task, subject, difficulty)")
                .eq("user_id", user_id)
                .eq("scheduled_date", today)
                .execute()
            )
            return res.data if res.data else []
        except Exception as e:
            logger.error(f"Error fetching today's tasks: {e}")
            return []

    def complete_session(self, session_id: int, task_id: int, hours_done: float, on_success=None):
        """Marks a session done and updates the parent Task's percentage."""
        try:
            self._supabase.table("schedule_items").update({"is_completed": True}).eq(
                "id", session_id
            ).execute()

            res = self._supabase.table("tasks").select("*").eq("id", task_id).single().execute()
            if res.data:
                task_obj = Task.from_dict(res.data)
                task_obj.mark_session_complete(hours_done)

                self._supabase.table("tasks").update({"completed": task_obj.completed_percent}).eq(
                    "id", task_id
                ).execute()
            self._supabase.rpc("check_and_increment_streak").execute()
            if on_success:
                on_success()
            return True
        except Exception as e:
            logger.error(f"Completion failed: {e}")
            return False

    def get_todays_sessions_as_objects(self, user_id: str) -> List[StudySession]:
        raw_data = self.get_todays_sessions(user_id)
        objects = []

        for d in raw_data:
            task_info = d.get("tasks", {})

            objects.append(
                StudySession(
                    id=d.get("id"),
                    task_id=d.get("task_id"),
                    title=task_info.get("task", "Untitled Task"),
                    subject=task_info.get("subject", "N/A"),
                    hours=d.get("hours_allocated", 0.0),
                    deadline=date.today(),
                    difficulty=task_info.get("difficulty", 3),
                    is_completed=d.get("is_completed", False),
                )
            )
        return objects

    def persist_single_session_and_get_id(self, user_id, session):
        """Saves a 'Draft' session from the scheduler into the DB on the fly."""
        res = (
            self._supabase.table("schedule_items")
            .insert(
                {
                    "user_id": user_id,
                    "task_id": session.task_id,
                    "scheduled_date": date.today().isoformat(),
                    "hours_allocated": session.hours,
                    "is_completed": False,
                }
            )
            .execute()
        )
        return res.data[0]["id"]

    def persist_single_session_and_get_id(self, user_id: str, session: StudySession) -> int:
        """Saves a draft session to DB and returns the new ID."""
        from services.scheduler import get_slot_date

        today_str = date.today().isoformat()

        res = (
            self._supabase.table("schedule_items")
            .insert(
                {
                    "user_id": user_id,
                    "task_id": session.task_id,
                    "scheduled_date": today_str,
                    "hours_allocated": session.hours,
                    "is_completed": False,
                }
            )
            .execute()
        )

        if res.data:
            return res.data[0]["id"]
        raise Exception("Failed to save session to database.")
