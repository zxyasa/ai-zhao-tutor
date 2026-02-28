from datetime import date, datetime, timedelta

from fastapi import HTTPException
from pydantic import ValidationError

from app.models import Achievement, DailySession, Event as DBEvent, Student
from app.schemas import EventCreate
from app.services.achievement_service import unlock_achievements
from app.routers.events import create_event
from app.services.event_processor import (
    update_daily_session_progress,
    update_student_streak,
)


def test_update_student_streak_progression(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()

    day1 = date(2026, 2, 18)
    day2 = date(2026, 2, 19)
    day4 = date(2026, 2, 21)

    update_student_streak(student, day1)
    assert student.current_streak == 1
    assert student.longest_streak == 1
    assert student.total_sessions == 1

    # Same day should not increase streak, only sessions.
    update_student_streak(student, day1)
    assert student.current_streak == 1
    assert student.longest_streak == 1
    assert student.total_sessions == 2

    update_student_streak(student, day2)
    assert student.current_streak == 2
    assert student.longest_streak == 2
    assert student.total_sessions == 3

    update_student_streak(student, day4)
    assert student.current_streak == 1
    assert student.longest_streak == 2
    assert student.total_sessions == 4


def test_achievement_unlocking_no_duplicates(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    student.current_streak = 3
    student.total_sessions = 20

    ts = datetime(2026, 2, 19, 8, 0, 0)
    daily_session = update_daily_session_progress(db_session, student, ts)
    daily_session.completed_questions = daily_session.target_questions
    daily_session.is_completed = True

    unlock_achievements(db_session, student, daily_session, ts)
    db_session.commit()
    assert db_session.query(Achievement).count() == 3

    # Re-running should not create duplicate badges.
    unlock_achievements(db_session, student, daily_session, ts)
    db_session.commit()
    assert db_session.query(Achievement).count() == 3

    # Meet streak_7 condition later.
    student.current_streak = 7
    unlock_achievements(db_session, student, daily_session, ts + timedelta(days=4))
    db_session.commit()
    assert db_session.query(Achievement).count() == 4


def test_create_event_validates_required_fields(db_session, seeded_students):
    try:
        EventCreate(student_id="jon_zhao")
        raise AssertionError("Expected ValidationError for missing fields")
    except ValidationError:
        pass


def test_create_event_student_not_found(db_session, seeded_students):
    payload = EventCreate(
        event_id="evt_missing_student",
        student_id="missing",
        item_id="item_1",
        answer_given="1",
        is_correct=True,
        time_spent=3.0,
    )
    try:
        import asyncio

        asyncio.run(
            create_event(
                event_data=payload,
                db=db_session,
                claims={"role": "student", "sub": "missing"},
            )
        )
        raise AssertionError("Expected HTTPException for missing student")
    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Student not found"


def test_update_daily_session_progress_creates_session(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    ts = datetime(2026, 2, 19, 7, 30, 0)
    session = update_daily_session_progress(db_session, student, ts)
    db_session.commit()

    persisted = db_session.query(DailySession).filter(DailySession.id == session.id).first()
    assert persisted is not None
    assert persisted.completed_questions == 1
    assert persisted.target_questions == student.target_daily_questions


def test_create_event_student_role_allows_missing_student_id(db_session, seeded_students):
    payload = EventCreate(
        event_id="evt_no_student_id",
        student_id=None,
        item_id="item_1",
        answer_given="1",
        is_correct=True,
        time_spent=2.5,
    )

    import asyncio

    result = asyncio.run(
        create_event(
            event_data=payload,
            db=db_session,
            claims={"role": "student", "sub": "jon_zhao"},
        )
    )
    assert result["status"] == "success"
    persisted = db_session.query(DBEvent).filter(DBEvent.id == "evt_no_student_id").first()
    assert persisted is not None
    assert persisted.student_id == "jon_zhao"
