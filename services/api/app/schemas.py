from datetime import datetime
from typing import Any, Optional

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


class NextItemResponse(BaseModel):
    """Shape returned by GET /next-item.

    Allows extra keys (e.g. dynamic-track metadata) so additions to the
    engine payload do not require a schema bump.
    """

    item_id: str
    skill_id: str
    question_text: str
    question_type: str
    difficulty: int
    parameters: dict
    correct_answer: str
    hint: Optional[str] = None
    explanation: str
    validation_rule: str
    # 9.1.2 graduation indicators (None on calls that don't graduate).
    graduated_to_index: Optional[int] = None
    graduated_to_label: Optional[str] = None
    # 9.1.4 worked example (only included on the student's first attempt for a skill).
    worked_example: Optional[dict[str, Any]] = None

    model_config = {"extra": "allow"}
