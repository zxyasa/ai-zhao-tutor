from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import DailySession as DBDailySession
from ..models import Event as DBEvent
from ..models import Student as DBStudent
from ..schemas import EventCreate
from .achievement_service import unlock_achievements
from .mastery_service import update_mastery_for_event


def process_event(db: Session, event_data: EventCreate) -> dict:
    student = db.query(DBStudent).filter(DBStudent.id == event_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    event_timestamp = parse_timestamp(event_data.timestamp)

    event = DBEvent(
        id=event_data.event_id,
        student_id=event_data.student_id,
        item_id=event_data.item_id,
        answer_given=event_data.answer_given,
        is_correct=event_data.is_correct,
        time_spent=event_data.time_spent,
        hint_requested=event_data.hint_requested,
        timestamp=event_timestamp,
    )
    db.add(event)

    update_student_streak(student, event_timestamp.date())
    daily_session = update_daily_session_progress(db, student, event_timestamp)
    update_mastery_for_event(
        db,
        student_id=event_data.student_id,
        item_id=event_data.item_id,
        is_correct=event_data.is_correct,
        updated_at=event_timestamp,
    )

    unlock_achievements(db, student, daily_session, event_timestamp)
    db.commit()

    return {"status": "success", "event_id": event.id}


def parse_timestamp(raw_value):
    if isinstance(raw_value, datetime):
        return raw_value
    if isinstance(raw_value, str):
        parsed = None
        try:
            parsed = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
        except ValueError:
            parsed = None
        if parsed:
            return parsed
    return datetime.now()


def update_student_streak(student: DBStudent, practice_date):
    previous_date = student.last_practice_date

    if previous_date is None:
        student.current_streak = 1
        student.last_practice_date = practice_date
    elif practice_date > previous_date:
        if practice_date == previous_date + timedelta(days=1):
            student.current_streak += 1
        else:
            student.current_streak = 1
        student.last_practice_date = practice_date

    student.longest_streak = max(student.longest_streak, student.current_streak)
    student.total_sessions += 1


def update_daily_session_progress(db: Session, student: DBStudent, event_timestamp: datetime):
    practice_date = event_timestamp.date()
    session = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date == practice_date,
    ).first()

    if not session:
        session = DBDailySession(
            id=str(uuid4()),
            student_id=student.id,
            session_date=practice_date,
            started_at=event_timestamp,
            completed_questions=0,
            target_questions=student.target_daily_questions,
            is_completed=False,
            completed_at=None,
        )
        db.add(session)

    if session.is_completed:
        session.bonus_questions += 1
    else:
        session.completed_questions += 1
        if session.completed_questions >= session.target_questions:
            session.is_completed = True
            session.completed_at = event_timestamp

    return session
