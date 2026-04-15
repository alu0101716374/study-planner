from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any
from lib.models import Task, StudySession

DAYS_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def get_slot_date(day_name: str) -> date:
    """Calculates the specific calendar date for a day of the week."""
    today = datetime.now(timezone.utc).date()
    today_idx = today.weekday() 
    target_idx = DAYS_ORDER.index(day_name)

    day_diff = target_idx - today_idx
    if day_diff < 0:
        day_diff += 7

    return today + timedelta(days=day_diff)


def split_tasks_into_sessions(tasks: List[Task]) -> List[StudySession]:
    """Breaks down high-level Tasks into manageable StudySessions."""
    sessions: List[StudySession] = []
    for task in tasks:
        remaining_time = task.remaining_hours()

        while remaining_time > 0:
            session_length = min(1.0, remaining_time)

            if session_length < 0.5 and sessions and sessions[-1].task_id == task.id:
                sessions[-1].hours += session_length
                remaining_time = 0
                break

            sessions.append(StudySession.from_task(task, session_length))
            remaining_time -= session_length

    return sessions


def violates_constraints(
    session: StudySession, day_name: str, schedule: Dict[str, List[StudySession]]
) -> bool:
    """Centralized check for all scheduling rules."""
    target_date = get_slot_date(day_name)

    if not session.is_due_after(target_date):
        return True

    if any(s.subject == session.subject for s in schedule[day_name]):
        return True

    day_idx = DAYS_ORDER.index(day_name)
    if day_idx > 0:
        prev_day = DAYS_ORDER[day_idx - 1]
        if any(s.subject == session.subject for s in schedule[prev_day]):
            return True

    return False


def generate_schedule(
    tasks_data: List[Task], availability: Dict[str, Any]
) -> Dict[str, List[StudySession]]:
    """The main orchestration engine."""
    tasks = tasks_data
    sessions = split_tasks_into_sessions(tasks)
    for s in sessions:
        s.calculate_priority()

    sessions.sort(key=lambda s: s.priority, reverse=True)
    schedule: Dict[str, List[StudySession]] = {day: [] for day in DAYS_ORDER}

    for day in DAYS_ORDER:
        available_hours = availability.get(day, {}).get("hours", 0)

        while available_hours > 0:
            found_fit = False
            for session in sessions:
                if session.is_assigned:
                    continue
                if not violates_constraints(session, day, schedule):
                    if session.hours <= available_hours:
                        session.is_assigned = True
                        schedule[day].append(session)
                        available_hours -= session.hours
                        found_fit = True
                        break
            if not found_fit:
                break

    unassigned = [s for s in sessions if not s.is_assigned]
    if unassigned:
        for day in DAYS_ORDER:
            used = sum(s.hours for s in schedule[day])
            total_avail = availability.get(day, {}).get("hours", 0)
            remaining_slots = total_avail - used

            for session in unassigned:
                if session.is_assigned:
                    continue

                if session.is_due_after(get_slot_date(day)) and session.hours <= remaining_slots:
                    session.is_assigned = True
                    schedule[day].append(session)
                    remaining_slots -= session.hours

    return schedule


def clean_for_ui(schedule: Dict[str, List[StudySession]]) -> Dict[str, List[StudySession]]:
    ui_schedule = {}

    for day, sessions in schedule.items():
        merged: Dict[str, StudySession] = {}

        for s in sessions:
            key = s.task_id

            if key in merged:
                merged[key].hours += s.hours
            else:
                merged[key] = StudySession(
                    task_id=s.task_id,
                    subject=s.subject,
                    hours=s.hours,
                    deadline=s.deadline,
                    difficulty=s.difficulty,
                    completed_percent=s.completed_percent,
                )

        ui_schedule[day] = list(merged.values())

    return ui_schedule