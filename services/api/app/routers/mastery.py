from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth.dependencies import get_token_claims, require_student_access
from ..database import get_db
from ..models import Mastery as DBMastery

router = APIRouter()


def _fetch_mastery_payload(db: Session, student_id: str) -> list[dict]:
    mastery_records = db.query(DBMastery).filter(
        DBMastery.student_id == student_id
    ).all()

    if not mastery_records:
        return []

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


@router.get("/mastery/{student_id}")
async def get_mastery(
    student_id: str,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    """
    Get all mastery data for a student.
    Returns mastery scores for all skills the student has attempted.
    """
    resolved_id = None if student_id == "me" else student_id
    student = require_student_access(db=db, claims=claims, student_id=resolved_id)
    return _fetch_mastery_payload(db, student.id)


@router.get("/mastery/me")
async def get_mastery_me(
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    student = require_student_access(db=db, claims=claims, student_id=None)
    return _fetch_mastery_payload(db, student.id)
