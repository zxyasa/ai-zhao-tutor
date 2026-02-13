from pydantic import BaseModel
from datetime import datetime


class Event(BaseModel):
    event_id: str
    student_id: str
    item_id: str
    answer_given: str
    is_correct: bool
    time_spent: float  # seconds
    hint_requested: bool = False
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_001",
                "student_id": "student_123",
                "item_id": "item_001_001",
                "answer_given": "3/5",
                "is_correct": True,
                "time_spent": 12.5,
                "hint_requested": False,
                "timestamp": "2024-02-13T10:30:00"
            }
        }
