from pydantic import BaseModel, Field
from typing import Dict, Any


class Item(BaseModel):
    item_id: str
    skill_id: str
    question_text: str
    question_type: str  # "fraction", "numeric", "multiple_choice"
    difficulty: int = Field(ge=1, le=5)
    parameters: Dict[str, Any]  # randomized values used to generate the item
    correct_answer: str
    hint: str
    explanation: str
    validation_rule: str  # "exact_match", "equivalent_fraction", "numeric_range"

    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "item_001_001",
                "skill_id": "yr3_frac_compare_001",
                "question_text": "Which is larger: 3/5 or 2/5?",
                "question_type": "fraction",
                "difficulty": 1,
                "parameters": {"num1": 3, "num2": 2, "denom": 5},
                "correct_answer": "3/5",
                "hint": "When denominators are the same, compare the numerators",
                "explanation": "Since both fractions have denominator 5, we compare numerators: 3 > 2, so 3/5 > 2/5",
                "validation_rule": "exact_match"
            }
        }
