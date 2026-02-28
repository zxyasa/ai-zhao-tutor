from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth.dependencies import get_token_claims, require_student_access
from ..database import get_db
from ..models import Student as DBStudent

router = APIRouter()

def _serialize_student(student: DBStudent) -> dict:
    return {
        "id": student.id,
        "name": student.name,
        "year_level": student.year_level,
        "avatar": student.avatar,
        "target_daily_questions": student.target_daily_questions,
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "last_practice_date": student.last_practice_date.isoformat() if student.last_practice_date else None,
        "total_sessions": student.total_sessions,
        "created_at": student.created_at.isoformat(),
    }


@router.get("/students")
async def list_students(
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    role = claims.get("role")
    subject = claims.get("sub")

    if role == "parent":
        students = db.query(DBStudent).filter(DBStudent.parent_id == subject).order_by(DBStudent.name.asc()).all()
    elif role == "student":
        students = db.query(DBStudent).filter(DBStudent.id == subject).all()
    else:
        raise HTTPException(status_code=403, detail="Unsupported role")

    return [_serialize_student(student) for student in students]


@router.get("/students/{student_id}")
async def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    resolved_id = None if student_id == "me" else student_id
    student = require_student_access(db=db, claims=claims, student_id=resolved_id)
    return _serialize_student(student)


@router.get("/streak/{student_id}")
async def get_streak(
    student_id: str,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    resolved_id = None if student_id == "me" else student_id
    student = require_student_access(db=db, claims=claims, student_id=resolved_id)

    today = date.today()
    last_practice_date = student.last_practice_date
    if last_practice_date is None:
        days_since = None
        practiced_today = False
        streak_at_risk = False
    else:
        days_since = (today - last_practice_date).days
        practiced_today = days_since == 0
        streak_at_risk = days_since >= 1 and student.current_streak > 0

    return {
        "student_id": student.id,
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "last_practice_date": last_practice_date.isoformat() if last_practice_date else None,
        "practiced_today": practiced_today,
        "days_since_last_practice": days_since,
        "is_streak_at_risk": streak_at_risk,
    }


@router.get("/streak/me")
async def get_streak_me(
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    student = require_student_access(db=db, claims=claims, student_id=None)

    today = date.today()
    last_practice_date = student.last_practice_date
    if last_practice_date is None:
        days_since = None
        practiced_today = False
        streak_at_risk = False
    else:
        days_since = (today - last_practice_date).days
        practiced_today = days_since == 0
        streak_at_risk = days_since >= 1 and student.current_streak > 0

    return {
        "student_id": student.id,
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "last_practice_date": last_practice_date.isoformat() if last_practice_date else None,
        "practiced_today": practiced_today,
        "days_since_last_practice": days_since,
        "is_streak_at_risk": streak_at_risk,
    }
