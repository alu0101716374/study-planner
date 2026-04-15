from typing import List, Optional, Dict, Any
from lib.models import Task
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
            return res.status_code == 204
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
            # Ensure we extract the 'availability' key if it exists in res.data
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
