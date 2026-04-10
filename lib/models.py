from dataclasses import dataclass, field
from datetime import datetime, date, timezone
from typing import Optional
from lib.logger import logger

@dataclass
class Task:
    id: Optional[int]
    user_id: str
    title: str
    subject: str
    hours: float
    deadline: Optional[datetime]
    difficulty: int
    completed_percent: int = 0
    description: Optional[str] = None

    def __post_init__(self):
        logger.info("Building Task object with data: %s", self.__dict__)
        if not self.title or len(self.title.strip()) == 0:
            logger.error("Task title cannot be empty")
            raise ValueError("task title cannot be empty")
        if self.hours < 0:
            logger.error("Task hours cannot be negative")
            raise ValueError("Task hours cannot be negative")
        if self.difficulty < 1 or self.difficulty > 5:
            logger.error("Task difficulty must be between 1 and 5")
            raise ValueError("Task difficulty must be between 1 and 5")
        if self.completed_percent < 0 or self.completed_percent > 100:
            logger.error("Task completed_percent must be between 0 and 100")
            raise ValueError("Task completed_percent must be between 0 and 100")        
        
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        raw_deadline = data.get("deadline")
        parsed_deadline: Optional[datetime] = None

        if isinstance(raw_deadline, str):
            try:
                parsed_deadline = datetime.fromisoformat(raw_deadline)
            except ValueError as e:
                logger.error(f"Warning: Could not parse deadline '{raw_deadline}' as ISO datetime: {e}")
                parsed_deadline = None
        elif isinstance(raw_deadline, datetime):
            parsed_deadline = raw_deadline
        elif raw_deadline is None:
            parsed_deadline = None
        else:
            logger.error(f"Deadline must be a string, datetime object, or None, got type {type(raw_deadline)} with value '{raw_deadline}'.")
            raise TypeError(f"Deadline must be a string, datetime object, or None, got type {type(raw_deadline)} with value '{raw_deadline}'.")
        
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            title=data.get("task"),
            subject=data.get("subject"),
            hours=float(data.get("hours", 0)),
            deadline=parsed_deadline, 
            difficulty=data.get("difficulty", 3),
            completed_percent=data.get("completed", 0),
            description=data.get("description")
        )

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "task": self.title,
            "subject": self.subject,
            "hours": self.hours,
            "deadline": self.deadline.isoformat() if self.deadline else None, 
            "completed": self.completed_percent,
            "description": self.description,
            "difficulty": self.difficulty
        }
    
    def remaining_hours(self) -> float:
        return (100 - self.completed_percent) / 100 * self.hours
    
@dataclass
class StudySession:
    URGENCY_WEIGHT = 0.5
    WORK_WEIGHT = 0.3
    DIFFICULTY_WEIGHT = 0.2 
    
    task_id: Optional[int] 
    subject: str
    hours: float
    deadline: date 
    difficulty: int
    completed_percent: int
    priority: float = field(init=False, default=0.0)
    is_assigned: bool = field(default=False) 

    @classmethod
    def from_task(cls, task: Task, hours: float) -> "StudySession":
        if task.id is None:
            logger.error("Cannot create StudySession from a Task with no ID.")
            raise ValueError("Cannot create StudySession from a Task with no ID.")
        if task.deadline is None:
            logger.error("Cannot create StudySession from a Task with no deadline.")
            raise ValueError("Cannot create StudySession from a Task with no deadline.")

        return cls(
            task_id=task.id, 
            subject=task.subject,
            hours=hours,
            deadline=task.deadline.date(),
            difficulty=task.difficulty,
            completed_percent=task.completed_percent
        )

    def is_due_after(self, target_date: date) -> bool:
        return target_date <= self.deadline
        
    def calculate_priority(self) -> None:
        today = datetime.now(timezone.utc).date()
        
        # Straight subtraction of date objects
        days_remaining = (self.deadline - today).days
        days_remaining = max(0, days_remaining)
        
        urgency = 1 / (days_remaining + 2)
        if days_remaining <= 2:
            urgency += 0.5
        
        remaining_work = 1 - (self.completed_percent / 100)
        
        self.priority = (
            (self.URGENCY_WEIGHT * urgency) + 
            (self.WORK_WEIGHT * remaining_work) + 
            (self.DIFFICULTY_WEIGHT * self.difficulty)
        )