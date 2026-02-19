from datetime import date, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import DailySession as DBDailySession, Student as DBStudent

router = APIRouter()


@router.post("/daily-session/start")
async def start_daily_session(student_id: str, db: Session = Depends(get_db)):
    student = db.query(DBStudent).filter(DBStudent.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    today = date.today()
    session = db.query(DBDailySession).filter(
        DBDailySession.student_id == student_id,
        DBDailySession.session_date == today,
    ).first()

    if not session:
        session = DBDailySession(
            id=str(uuid4()),
            student_id=student_id,
            session_date=today,
            started_at=datetime.now(),
            completed_questions=0,
            target_questions=student.target_daily_questions,
            is_completed=False,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    return _serialize_daily_session(session)


@router.get("/daily-session/status/{student_id}")
async def get_daily_session_status(student_id: str, db: Session = Depends(get_db)):
    student = db.query(DBStudent).filter(DBStudent.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    today = date.today()
    session = db.query(DBDailySession).filter(
        DBDailySession.student_id == student_id,
        DBDailySession.session_date == today,
    ).first()

    if not session:
        return {
            "student_id": student_id,
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
