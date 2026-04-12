import pytest
from datetime import datetime, timedelta, timezone
from lib.models import Task, StudySession, ScheduleItem
from services.scheduler import get_slot_date, split_tasks_into_sessions, violates_constraints, generate_schedule, clean_for_ui, DAYS_ORDER


def test_get_slot_date_returns_correct_weekday():
    today = datetime.now(timezone.utc).date()
    today_name = DAYS_ORDER[today.weekday()]
    result = get_slot_date(today_name)
    assert result.weekday() == today.weekday()
    assert result >= today


def test_split_tasks_into_sessions_breaks_into_hour_blocks():
    future_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    task = Task(
        id=1,
        user_id="user123",
        title="Study Python",
        subject="Programming",
        hours=2.5,
        deadline=future_deadline,
        difficulty=3,
        completed_percent=0,
        description="Practice"
    )

    sessions = split_tasks_into_sessions([task])
    assert len(sessions) == 3
    assert sum(s.hours for s in sessions) == pytest.approx(2.5)
    assert sessions[-1].hours == 0.5
    assert all(session.task_id == 1 for session in sessions)


def test_split_tasks_into_sessions_merges_small_remainder():
    future_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    task = Task(
        id=2,
        user_id="user123",
        title="Read",
        subject="History",
        hours=1.4,
        deadline=future_deadline,
        difficulty=2,
        completed_percent=0,
        description="Reading"
    )

    sessions = split_tasks_into_sessions([task])
    assert len(sessions) == 1
    assert sessions[0].hours == pytest.approx(1.4)


def test_violates_constraints_due_date_and_subject():
    future_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    task = Task(
        id=3,
        user_id="user123",
        title="Physics",
        subject="Science",
        hours=1.0,
        deadline=future_deadline,
        difficulty=3,
        completed_percent=0,
        description="Chapter 1"
    )
    session = StudySession.from_task(task, 1.0)

    schedule = {day: [] for day in DAYS_ORDER}
    day_name = DAYS_ORDER[0]
    assert violates_constraints(session, day_name, schedule) is False

    schedule[day_name].append(session)
    assert violates_constraints(session, day_name, schedule) is True

    next_day = DAYS_ORDER[1]
    assert violates_constraints(session, next_day, schedule) is True


def test_clean_for_ui_merges_same_subject_sessions():
    future_deadline = (datetime.now(timezone.utc) + timedelta(days=30)).date()
    schedule = {
        "monday": [
            StudySession(task_id=1, subject="Math", hours=1.0, deadline=future_deadline, difficulty=2, completed_percent=0),
            StudySession(task_id=1, subject="Math", hours=0.5, deadline=future_deadline, difficulty=2, completed_percent=0),
        ],
        "tuesday": []
    }
    merged = clean_for_ui(schedule)
    assert merged["monday"][0].hours == pytest.approx(1.5)
    assert merged["monday"][0].subject == "Math"


def test_generate_schedule_respects_availability_and_fallback():
    future_deadline_1 = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    future_deadline_2 = (datetime.now(timezone.utc) + timedelta(days=31)).isoformat()
    tasks_dicts = [
        {
            "id": 1,
            "user_id": "user123",
            "task": "Study Math",
            "subject": "Math",
            "hours": 2.0,
            "deadline": future_deadline_1,
            "difficulty": 3,
            "completed": 0,
            "description": "Practice"
        },
        {
            "id": 2,
            "user_id": "user123",
            "task": "Study English",
            "subject": "English",
            "hours": 2.0,
            "deadline": future_deadline_2,
            "difficulty": 2,
            "completed": 0,
            "description": "Essay"
        }
    ]
    tasks_data = [Task.from_dict(task_dict) for task_dict in tasks_dicts]
    availability = {day: {"hours": 1} for day in DAYS_ORDER}

    schedule = generate_schedule(tasks_data, availability)
    assert isinstance(schedule, dict)
    assert all(isinstance(schedule[day], list) for day in DAYS_ORDER)
    assert all(isinstance(item, ScheduleItem) for day in DAYS_ORDER for item in schedule[day])
    assert sum(item.hours for day in DAYS_ORDER for item in schedule[day]) == pytest.approx(4.0)
