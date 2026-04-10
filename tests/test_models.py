import pytest
from datetime import datetime, timezone
from lib.models import Task, StudySession


class TestTask:
    """Test cases for the Task dataclass."""

    def test_from_dict_valid(self):
        """Test creating Task from valid dict."""
        data = {
            "id": 1,
            "user_id": "user123",
            "task": "Study Math",
            "subject": "Mathematics",
            "hours": 5.0,
            "deadline": "2026-04-15T10:00:00",
            "completed": 50,
            "description": "Chapter 5",
            "difficulty": 3
        }
        task = Task.from_dict(data)
        assert task.id == 1
        assert task.title == "Study Math"
        assert task.hours == 5.0
        assert task.completed_percent == 50

    def test_from_dict_invalid_title(self):
        """Test Task creation fails with empty title."""
        data = {
            "user_id": "user123",
            "task": "",  # Invalid
            "subject": "Math",
            "hours": 2.0,
            "deadline": None,
            "completed": 0,
            "difficulty": 2
        }
        with pytest.raises(ValueError, match="task title cannot be empty"):
            Task.from_dict(data)

    def test_from_dict_negative_hours(self):
        """Test Task creation fails with negative hours."""
        data = {
            "user_id": "user123",
            "task": "Study",
            "subject": "Math",
            "hours": -1.0,  # Invalid
            "deadline": None,
            "completed": 0,
            "difficulty": 2
        }
        with pytest.raises(ValueError, match="Task hours cannot be negative"):
            Task.from_dict(data)

    def test_to_dict(self):
        """Test converting Task to dict."""
        deadline = datetime(2026, 4, 15, 10, 0, tzinfo=timezone.utc)
        task = Task(
            id=1,
            user_id="user123",
            title="Study Math",
            subject="Mathematics",
            hours=5.0,
            deadline=deadline,
            difficulty=3,
            completed_percent=50,
            description="Chapter 5"
        )
        data = task.to_dict()
        assert data["user_id"] == "user123"
        assert data["task"] == "Study Math"
        assert data["hours"] == 5.0
        assert data["deadline"] == "2026-04-15T10:00:00+00:00"

    def test_remaining_hours(self):
        """Test calculating remaining hours."""
        task = Task(
            id=1,
            user_id="user123",
            title="Study",
            subject="Math",
            hours=10.0,
            deadline=None,
            difficulty=2,
            completed_percent=30
        )
        assert task.remaining_hours() == 7.0  # 70% of 10


class TestStudySession:
    """Test cases for StudySession."""

    def test_from_task_valid(self):
        """Test creating StudySession from Task."""
        deadline = datetime(2026, 4, 15, tzinfo=timezone.utc)
        task = Task(
            id=1,
            user_id="user123",
            title="Study",
            subject="Math",
            hours=10.0,
            deadline=deadline,
            difficulty=2,
            completed_percent=30
        )
        session = StudySession.from_task(task, 2.0)
        assert session.task_id == 1
        assert session.subject == "Math"
        assert session.hours == 2.0
        assert session.deadline == deadline.date()

    def test_from_task_no_id(self):
        """Test StudySession creation fails without Task ID."""
        task = Task(
            id=None,  # Invalid
            user_id="user123",
            title="Study",
            subject="Math",
            hours=10.0,
            deadline=datetime(2026, 4, 15, tzinfo=timezone.utc),
            difficulty=2,
            completed_percent=30
        )
        with pytest.raises(ValueError, match="Cannot create StudySession from a Task with no ID"):
            StudySession.from_task(task, 2.0)

    def test_from_task_no_deadline(self):
        """Test StudySession creation fails without deadline."""
        task = Task(
            id=1,
            user_id="user123",
            title="Study",
            subject="Math",
            hours=10.0,
            deadline=None,  # Invalid
            difficulty=2,
            completed_percent=30
        )
        with pytest.raises(ValueError, match="Cannot create StudySession from a Task with no deadline"):
            StudySession.from_task(task, 2.0)

    def test_calculate_priority(self):
        """Test priority calculation."""
        session = StudySession(
            task_id=1,
            subject="Math",
            hours=2.0,
            deadline=datetime(2026, 4, 15, tzinfo=timezone.utc).date(),
            difficulty=3,
            completed_percent=50
        )
        session.calculate_priority()
        # Priority should be calculated based on weights
        assert isinstance(session.priority, float)
        assert session.priority > 0