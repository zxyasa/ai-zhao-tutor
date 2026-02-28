from datetime import date, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth.dependencies import get_token_claims, require_student_access
from ..database import get_db
from ..models import DailySession as DBDailySession

router = APIRouter()


@router.post("/daily-session/start")
async def start_daily_session(
    student_id: str | None = None,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    student = require_student_access(db=db, claims=claims, student_id=student_id)
    target_student_id = student.id

    today = date.today()
    session = db.query(DBDailySession).filter(
        DBDailySession.student_id == target_student_id,
        DBDailySession.session_date == today,
    ).first()

    if not session:
        session = DBDailySession(
            id=str(uuid4()),
            student_id=target_student_id,
            session_date=today,
            started_at=datetime.now(),
            completed_questions=0,
            target_questions=student.target_daily_questions,
            is_completed=False,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    elif session.target_questions != student.target_daily_questions:
        # 如果学生每日目标已调整（如 Jon 改为 40），同步到当天 session。
        session.target_questions = student.target_daily_questions
        db.commit()
        db.refresh(session)

    return _serialize_daily_session(session)


@router.get("/daily-session/status/{student_id}")
async def get_daily_session_status(
    student_id: str,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    resolved_id = None if student_id == "me" else student_id
    student = require_student_access(db=db, claims=claims, student_id=resolved_id)

    today = date.today()
    session = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date == today,
    ).first()

    if not session:
        return {
            "student_id": student.id,
            "session_date": today.isoformat(),
            "completed_questions": 0,
            "target_questions": student.target_daily_questions,
            "is_completed": False,
            "started_at": None,
            "completed_at": None,
            "current_streak": student.current_streak,
            "longest_streak": student.longest_streak,
        }

    payload = _serialize_daily_session(session)
    payload["current_streak"] = student.current_streak
    payload["longest_streak"] = student.longest_streak
    return payload


@router.get("/daily-session/status")
async def get_daily_session_status_me(
    student_id: str | None = None,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    student = require_student_access(db=db, claims=claims, student_id=student_id)
    today = date.today()
    session = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date == today,
    ).first()

    if not session:
        return {
            "student_id": student.id,
            "session_date": today.isoformat(),
            "completed_questions": 0,
            "target_questions": student.target_daily_questions,
            "is_completed": False,
            "started_at": None,
            "completed_at": None,
            "current_streak": student.current_streak,
            "longest_streak": student.longest_streak,
        }

    payload = _serialize_daily_session(session)
    payload["current_streak"] = student.current_streak
    payload["longest_streak"] = student.longest_streak
    return payload


def _serialize_daily_session(session: DBDailySession) -> dict:
    return {
        "id": session.id,
        "student_id": session.student_id,
        "session_date": session.session_date.isoformat(),
        "started_at": session.started_at.isoformat(),
        "completed_questions": session.completed_questions,
        "target_questions": session.target_questions,
        "is_completed": session.is_completed,
        "completed_at": session.completed_at.isoformat() if session.completed_at else None,
    }
