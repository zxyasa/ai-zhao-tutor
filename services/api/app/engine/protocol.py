from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SelectionRequest:
    student_id: str
    skill_id: Optional[str] = None
    year_level: Optional[int] = None
    engine_hint: Optional[str] = None


@dataclass
class SelectionResult:
    item_id: str
    skill_id: str
    question_text: str
    question_type: str
    difficulty: int
    correct_answer: str
    hint: str
    explanation: str
    parameters: dict = field(default_factory=dict)
    validation_rule: str = "numeric"
    # Internal metadata for analysis/debugging.
    selection_reason: str = "unknown"
    difficulty_delta: int = 0
