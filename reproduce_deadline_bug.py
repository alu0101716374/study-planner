from datetime import datetime, timedelta, timezone
from lib.models import Task

def reproduce_bug():
    past_deadline = datetime.now(timezone.utc) - timedelta(days=1)
    print(f"Attempting to create a task with a past deadline: {past_deadline}")
    
    try:
        # This represents a task being loaded from the database
        task = Task(
            id=101,
            user_id="user_1",
            title="Expired Task",
            subject="Math",
            hours=2.0,
            deadline=past_deadline,
            difficulty=3
        )
        print("Successfully created task (unexpected!)")
    except ValueError as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    reproduce_bug()
