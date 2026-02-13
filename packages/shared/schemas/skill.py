from pydantic import BaseModel, Field
from typing import List


class Skill(BaseModel):
    skill_id: str
    description: str
    year_level: int = Field(ge=3, le=6)
    domain: str  # "Number & Algebra", "Fractions"
    prerequisites: List[str] = Field(default_factory=list)
    difficulty_levels: List[int] = Field(default=[1, 2, 3, 4, 5])
    common_misconceptions: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "skill_id": "yr3_frac_intro_001",
                "description": "Understand fractions as equal parts of a whole",
                "year_level": 3,
                "domain": "Fractions",
                "prerequisites": [],
                "difficulty_levels": [1, 2, 3, 4, 5],
                "common_misconceptions": [
                    "Larger denominator means larger fraction",
                    "Fractions must always be less than 1"
                ]
            }
        }
