from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
sys.path.append("../../packages/shared")

from ..database import get_db
from ..models import Mastery as DBMastery

router = APIRouter()


@router.get("/mastery/{student_id}")
async def get_mastery(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all mastery data for a student.
    Returns mastery scores for all skills the student has attempted.
    """
    mastery_records = db.query(DBMastery).filter(
        DBMastery.student_id == student_id
    ).all()

    if not mastery_records:
        return []

    # Convert to response format
    result = []
    for record in mastery_records:
        result.append({
            "student_id": record.student_id,
            "skill_id": record.skill_id,
            "total_attempts": record.total_attempts,
            "correct_attempts": record.correct_attempts,
            "mastery_score": record.mastery_score,
            "last_updated": record.last_updated.isoformat()
        })

    return result
