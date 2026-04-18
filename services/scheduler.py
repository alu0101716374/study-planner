from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any, Optional
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
    """Breaks down high-level Tasks into manageable StudySessions. (Original logic - now used for new sessions)"""
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

    if any(
        s.subject == session.subject and s.task_id != session.task_id for s in schedule[day_name]
    ):
        return True

    day_idx = DAYS_ORDER.index(day_name)
    if day_idx > 0:
        prev_day = DAYS_ORDER[day_idx - 1]
        if any(
            s.subject == session.subject and s.task_id != session.task_id
            for s in schedule[prev_day]
        ):
            return True

    return False


def generate_schedule(
    tasks_data: List[Task],
    availability: Dict[str, Any],
    existing_scheduled_sessions: Optional[Dict[date, List[StudySession]]] = None,
) -> Dict[str, List[StudySession]]:
    """The main orchestration engine, now considering existing scheduled sessions."""
    task_map = {task.id: task for task in tasks_data}
    schedule: Dict[str, List[StudySession]] = {day: [] for day in DAYS_ORDER}

    unassigned_task_hours: Dict[int, float] = {
        task.id: task.remaining_hours() for task in tasks_data
    }

    if existing_scheduled_sessions:
        for day_name in DAYS_ORDER:
            current_date = get_slot_date(day_name)
            if current_date in existing_scheduled_sessions:
                for session in existing_scheduled_sessions[current_date]:
                    task = task_map.get(session.task_id)
                    if task:
                        session.subject = task.subject
                        session.deadline = task.deadline.date() if task.deadline else None
                        session.difficulty = task.difficulty

                        if session.id is None and "id" in getattr(session, "_data", {}):
                            session.id = session._data["id"]

    new_potential_sessions: List[StudySession] = []
    for task in tasks_data:
        remaining_time_to_schedule = unassigned_task_hours.get(task.id, 0.0)
        if remaining_time_to_schedule > 0:
            current_task_remaining = remaining_time_to_schedule
            while current_task_remaining > 0:
                session_length = min(1.0, current_task_remaining)
                temp_session = StudySession.from_task(task, session_length)
                temp_session.is_assigned = False
                new_potential_sessions.append(temp_session)
                current_task_remaining -= session_length

    sessions_to_assign = new_potential_sessions
    for s in sessions_to_assign:
        s.calculate_priority()

    sessions_to_assign.sort(key=lambda s: s.priority, reverse=True)

    for day in DAYS_ORDER:
        hours_filled_on_day = sum(s.hours for s in schedule[day])

        available_hours = availability.get(day, {}).get("hours", 0) - hours_filled_on_day
        if available_hours < 0:
            available_hours = 0.0

        while available_hours > 0:
            found_fit = False
            for session in sessions_to_assign:
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

    unassigned_new_sessions = [s for s in sessions_to_assign if not s.is_assigned]
    if unassigned_new_sessions:
        for day in DAYS_ORDER:
            used = sum(s.hours for s in schedule[day])
            total_avail = availability.get(day, {}).get("hours", 0)
            remaining_slots = total_avail - used
            if remaining_slots < 0:
                remaining_slots = 0.0

            for session in unassigned_new_sessions:
                if session.is_assigned:
                    continue

                if session.is_due_after(get_slot_date(day)) and session.hours <= remaining_slots:
                    session.is_assigned = True
                    schedule[day].append(session)
                    remaining_slots -= session.hours
    print(schedule)

    return schedule


def clean_for_ui(schedule: Dict[str, List[StudySession]]) -> Dict[str, List[StudySession]]:
    ui_schedule = {}
    for day, sessions in schedule.items():
        merged: Dict[str, StudySession] = {}
        for s in sessions:
            key = f"{s.task_id}-{s.subject}"
            if key in merged:
                merged[key].hours += s.hours
                merged[key].id = merged[key].id or s.id
            else:
                merged[key] = StudySession(
                    id=s.id,
                    task_id=s.task_id,
                    subject=s.subject,
                    hours=s.hours,
                    deadline=s.deadline,
                    difficulty=s.difficulty,
                    completed_percent=s.completed_percent,
                    is_assigned=s.is_assigned,
                    is_completed=getattr(s, "is_completed", False),
                )
        ui_schedule[day] = list(merged.values())
    return ui_schedule
