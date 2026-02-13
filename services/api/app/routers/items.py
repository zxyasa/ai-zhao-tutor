from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import sys
sys.path.append("../../packages/shared")

from ..database import get_db
from ..models import Item as DBItem, Event as DBEvent, Mastery as DBMastery

router = APIRouter()


@router.get("/next-item")
async def get_next_item(
    student_id: str,
    skill_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Fetch next item for a student based on their mastery level.
    If skill_id is provided, filter items for that skill.
    Otherwise, select based on student's weakest skills.
    """
    # Get student's mastery data
    if skill_id:
        mastery = db.query(DBMastery).filter(
            DBMastery.student_id == student_id,
            DBMastery.skill_id == skill_id
        ).first()

        # Determine difficulty based on mastery score
        if mastery:
            if mastery.mastery_score < 0.3:
                target_difficulty = 1
            elif mastery.mastery_score < 0.5:
                target_difficulty = 2
            elif mastery.mastery_score < 0.7:
                target_difficulty = 3
            elif mastery.mastery_score < 0.9:
                target_difficulty = 4
            else:
                target_difficulty = 5
        else:
            # No mastery data, start with difficulty 1
            target_difficulty = 1

        # Fetch item with target difficulty
        item = db.query(DBItem).filter(
            DBItem.skill_id == skill_id,
            DBItem.difficulty == target_difficulty
        ).order_by(func.random()).first()
    else:
        # No skill specified - find weakest skill and provide item for it
        weakest_skill = db.query(DBMastery).filter(
            DBMastery.student_id == student_id
        ).order_by(DBMastery.mastery_score).first()

        if weakest_skill:
            skill_id = weakest_skill.skill_id
            item = db.query(DBItem).filter(
                DBItem.skill_id == skill_id
            ).order_by(func.random()).first()
        else:
            # Student has no mastery data - select any item
            item = db.query(DBItem).filter(
                DBItem.difficulty == 1
            ).order_by(func.random()).first()

    if not item:
        raise HTTPException(status_code=404, detail="No items available")

    # Convert to dict format matching Pydantic schema
    return {
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
    }
