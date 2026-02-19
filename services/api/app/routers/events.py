from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict
from uuid import uuid4
import sys
sys.path.append("../../packages/shared")

from ..database import get_db
from ..models import (
    Achievement as DBAchievement,
    Event as DBEvent,
    Mastery as DBMastery,
    Student as DBStudent,
    DailySession as DBDailySession,
)

router = APIRouter()


@router.post("/events")
async def create_event(
    event_data: Dict,
    db: Session = Depends(get_db)
):
    """
    Record a student answer event and update mastery scores.
    """
    missing_fields = [
        field
        for field in ["event_id", "student_id", "item_id", "answer_given", "is_correct", "time_spent"]
        if field not in event_data
    ]
    if missing_fields:
        raise HTTPException(status_code=400, detail=f"Missing fields: {', '.join(missing_fields)}")

    student = db.query(DBStudent).filter(DBStudent.id == event_data["student_id"]).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    event_timestamp = _parse_timestamp(event_data.get("timestamp"))

    # Create event
    event = DBEvent(
        id=event_data["event_id"],
        student_id=event_data["student_id"],
        item_id=event_data["item_id"],
        answer_given=event_data["answer_given"],
        is_correct=event_data["is_correct"],
        time_spent=event_data["time_spent"],
        hint_requested=event_data.get("hint_requested", False),
        timestamp=event_timestamp
    )

    db.add(event)
    _update_student_streak(student, event_timestamp.date())
    daily_session = _update_daily_session_progress(db, student, event_timestamp)

    # Update mastery
    # First get the skill_id from the item
    from ..models import Item as DBItem
    item = db.query(DBItem).filter(DBItem.id == event_data["item_id"]).first()

    if item:
        mastery = db.query(DBMastery).filter(
            DBMastery.student_id == event_data["student_id"],
            DBMastery.skill_id == item.skill_id
        ).first()

        if mastery:
            # Update existing mastery
            mastery.total_attempts += 1
            if event_data["is_correct"]:
                mastery.correct_attempts += 1
            mastery.mastery_score = mastery.correct_attempts / mastery.total_attempts
            mastery.last_updated = datetime.now()
        else:
            # Create new mastery record
            mastery = DBMastery(
                student_id=event_data["student_id"],
                skill_id=item.skill_id,
                total_attempts=1,
                correct_attempts=1 if event_data["is_correct"] else 0,
                mastery_score=1.0 if event_data["is_correct"] else 0.0,
                last_updated=datetime.now()
            )
            db.add(mastery)

    _unlock_achievements(db, student, daily_session, event_timestamp)
    db.commit()

    return {"status": "success", "event_id": event.id}


def _parse_timestamp(raw_value):
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


def _update_student_streak(student: DBStudent, practice_date):
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
    # Same day repeat attempts keep streak unchanged

    student.longest_streak = max(student.longest_streak, student.current_streak)
    student.total_sessions += 1


def _update_daily_session_progress(db: Session, student: DBStudent, event_timestamp: datetime):
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

    session.completed_questions += 1

    if (not session.is_completed) and session.completed_questions >= session.target_questions:
        session.is_completed = True
        session.completed_at = event_timestamp

    return session


BADGE_DEFS = {
    "streak_3": ("连续3天", "连续练习 3 天"),
    "streak_7": ("连续7天", "连续练习 7 天"),
    "daily_goal_1": ("今日达标", "首次完成每日目标"),
    "sessions_20": ("练习达人", "累计完成 20 次答题"),
}


def _unlock_achievements(db: Session, student: DBStudent, daily_session: DBDailySession, now: datetime):
    _maybe_grant_badge(db, student.id, "streak_3", student.current_streak >= 3, now)
    _maybe_grant_badge(db, student.id, "streak_7", student.current_streak >= 7, now)
    _maybe_grant_badge(db, student.id, "daily_goal_1", bool(daily_session and daily_session.is_completed), now)
    _maybe_grant_badge(db, student.id, "sessions_20", student.total_sessions >= 20, now)


def _maybe_grant_badge(db: Session, student_id: str, badge_key: str, condition: bool, unlocked_at: datetime):
    if not condition:
        return

    exists = db.query(DBAchievement).filter(
        DBAchievement.student_id == student_id,
        DBAchievement.badge_key == badge_key,
    ).first()
    if exists:
        return

    title, description = BADGE_DEFS[badge_key]
    db.add(
        DBAchievement(
            id=str(uuid4()),
            student_id=student_id,
            badge_key=badge_key,
            title=title,
            description=description,
            unlocked_at=unlocked_at,
        )
    )
