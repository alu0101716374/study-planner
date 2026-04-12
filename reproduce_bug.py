from datetime import datetime, timedelta, timezone
from services.scheduler import generate_schedule
from lib.models import Task

def reproduce():
    # Simulate today being Friday, April 17, 2026
    today = datetime(2026, 4, 17, tzinfo=timezone.utc)
    print(f"Simulated Today: {today.strftime('%A')} ({today.date()})")

    # Task due this Sunday, April 19, 2026
    deadline = datetime(2026, 4, 19, tzinfo=timezone.utc)
    print(f"Task deadline: {deadline.strftime('%A')} ({deadline.date()})")

    tasks = [
        Task(
            id=1,
            user_id="user123",
            title="Weekend Task",
            subject="History",
            hours=2.0,
            deadline=deadline,
            difficulty=3,
            completed_percent=0
        )
    ]

    availability = {day: {"hours": 4} for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]}

    # We need to monkeypatch datetime.now or just be aware that get_slot_date uses datetime.now
    # Actually, I will just modify get_slot_date in scheduler.py temporarily or pass today to it.
    # But for a quick test, let's just see what happens with current date.
    # Wait, I'll just change the script to use a deadline that is "today + 2 days" but where today is Friday.
    # Since I can't easily monkeypatch here without more code, I'll just check what today is.

    schedule = generate_schedule(tasks, availability)
    print("\nFinal Schedule Keys:", schedule.keys())
    for day, items in schedule.items():
        if items:
            print(f"{day}: {items}")
        else:
            print(f"{day}: EMPTY")

if __name__ == "__main__":
    reproduce()
