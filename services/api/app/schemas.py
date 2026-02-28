from datetime import datetime

from pydantic import BaseModel


class EventCreate(BaseModel):
    event_id: str
    student_id: str | None = None
    item_id: str
    answer_given: str
    is_correct: bool
    time_spent: float
    hint_requested: bool = False
    timestamp: datetime | None = None
