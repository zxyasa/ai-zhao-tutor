from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Achievement as DBAchievement, DailySession as DBDailySession, Event as DBEvent, Student as DBStudent

router = APIRouter()


@router.get("/parent/daily-summary")
async def get_parent_daily_summary(db: Session = Depends(get_db)):
    today = date.today()
    students = db.query(DBStudent).order_by(DBStudent.name.asc()).all()
    return [_build_student_daily_summary(db, student, today) for student in students]


@router.get("/parent/daily-summary/{student_id}")
async def get_parent_daily_summary_for_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(DBStudent).filter(DBStudent.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return _build_student_daily_summary(db, student, date.today())


@router.get("/parent/weekly-summary")
async def get_parent_weekly_summary(db: Session = Depends(get_db)):
    today = date.today()
    start_day = today - timedelta(days=6)

    students = db.query(DBStudent).order_by(DBStudent.name.asc()).all()
    return [_build_student_weekly_summary(db, student, start_day, today) for student in students]


def _build_student_daily_summary(db: Session, student: DBStudent, day: date) -> dict:
    start_dt = datetime.combine(day, time.min)
    end_dt = datetime.combine(day, time.max)

    events = db.query(DBEvent).filter(
        DBEvent.student_id == student.id,
        DBEvent.timestamp >= start_dt,
        DBEvent.timestamp <= end_dt,
    ).all()

    correct_count = sum(1 for event in events if event.is_correct)
    total_count = len(events)
    accuracy = round((correct_count / total_count) * 100, 1) if total_count else 0.0
    avg_time = round(sum(event.time_spent for event in events) / total_count, 2) if total_count else 0.0

    session = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date == day,
    ).first()

    completed_questions = session.completed_questions if session else 0
    target_questions = session.target_questions if session else student.target_daily_questions
    is_completed = session.is_completed if session else False
    badge_count = db.query(DBAchievement).filter(DBAchievement.student_id == student.id).count()

    return {
        "student_id": student.id,
        "student_name": student.name,
        "avatar": student.avatar,
        "session_date": day.isoformat(),
        "completed_questions": completed_questions,
        "target_questions": target_questions,
        "is_completed": is_completed,
        "events_total": total_count,
        "correct_answers": correct_count,
        "accuracy_percent": accuracy,
        "average_time_spent_seconds": avg_time,
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "badge_count": badge_count,
    }


def _build_student_weekly_summary(db: Session, student: DBStudent, start_day: date, end_day: date) -> dict:
    start_dt = datetime.combine(start_day, time.min)
    end_dt = datetime.combine(end_day, time.max)

    events = db.query(DBEvent).filter(
        DBEvent.student_id == student.id,
        DBEvent.timestamp >= start_dt,
        DBEvent.timestamp <= end_dt,
    ).all()
    total_events = len(events)
    correct_events = sum(1 for event in events if event.is_correct)
    accuracy = round((correct_events / total_events) * 100, 1) if total_events else 0.0

    sessions = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date >= start_day,
        DBDailySession.session_date <= end_day,
    ).all()

    completed_days = sum(1 for session in sessions if session.is_completed)
    total_completed_questions = sum(session.completed_questions for session in sessions)

    return {
        "student_id": student.id,
        "student_name": student.name,
        "avatar": student.avatar,
        "from_date": start_day.isoformat(),
        "to_date": end_day.isoformat(),
        "completed_days": completed_days,
        "total_completed_questions": total_completed_questions,
        "total_events": total_events,
        "accuracy_percent": accuracy,
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
    }
