from pydantic import BaseModel, Field
from datetime import datetime


class Mastery(BaseModel):
    student_id: str
    skill_id: str
    total_attempts: int = Field(ge=0, default=0)
    correct_attempts: int = Field(ge=0, default=0)
    mastery_score: float = Field(ge=0.0, le=1.0, default=0.0)
    last_updated: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_123",
                "skill_id": "yr3_frac_compare_001",
                "total_attempts": 10,
                "correct_attempts": 8,
                "mastery_score": 0.8,
                "last_updated": "2024-02-13T10:30:00"
            }
        }
