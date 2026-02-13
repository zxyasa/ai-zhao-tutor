from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import sys
sys.path.append("../../packages/shared")

from ..database import get_db
from ..models import Item as DBItem

router = APIRouter()


@router.post("/placement/start")
async def start_placement_test(
    student_id: str,
    year_level: int,
    db: Session = Depends(get_db)
):
    """
    Start a placement test for a student.
    Returns a sequence of items across different skills and difficulty levels.
    """
    if year_level < 3 or year_level > 6:
        raise HTTPException(status_code=400, detail="Year level must be between 3 and 6")

    # Fetch items across difficulty levels (1-5) with variety
    # For placement test: 2 items per difficulty level = 10 total items
    items = []

    for difficulty in range(1, 6):
        difficulty_items = db.query(DBItem).filter(
            DBItem.difficulty == difficulty
        ).order_by(func.random()).limit(2).all()

        for item in difficulty_items:
            items.append({
                "item_id": item.id,
                "skill_id": item.skill_id,
                "question_text": item.question_text,
                "question_type": item.question_type,
                "difficulty": item.difficulty,
                "parameters": item.parameters,
                "correct_answer": item.correct_answer,
                "hint": item.hint,
                "explanation": item.explanation,
                "validation_rule": item.validation_rule
            })

    if not items:
        raise HTTPException(status_code=404, detail="No placement test items available")

    return {
        "student_id": student_id,
        "year_level": year_level,
        "items": items,
        "total_items": len(items)
    }
