from datetime import date, datetime, timedelta

from fastapi import HTTPException

from app.models import Achievement, DailySession, Student
from app.routers.events import (
    _unlock_achievements,
    _update_daily_session_progress,
    _update_student_streak,
    create_event,
)


def test_update_student_streak_progression(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()

    day1 = date(2026, 2, 18)
    day2 = date(2026, 2, 19)
    day4 = date(2026, 2, 21)

    _update_student_streak(student, day1)
    assert student.current_streak == 1
    assert student.longest_streak == 1
    assert student.total_sessions == 1

    # Same day should not increase streak, only sessions.
    _update_student_streak(student, day1)
    assert student.current_streak == 1
    assert student.longest_streak == 1
    assert student.total_sessions == 2

    _update_student_streak(student, day2)
    assert student.current_streak == 2
    assert student.longest_streak == 2
    assert student.total_sessions == 3

    _update_student_streak(student, day4)
    assert student.current_streak == 1
    assert student.longest_streak == 2
    assert student.total_sessions == 4


def test_achievement_unlocking_no_duplicates(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    student.current_streak = 3
    student.total_sessions = 20

    ts = datetime(2026, 2, 19, 8, 0, 0)
    daily_session = _update_daily_session_progress(db_session, student, ts)
    daily_session.completed_questions = daily_session.target_questions
    daily_session.is_completed = True

    _unlock_achievements(db_session, student, daily_session, ts)
    db_session.commit()
    assert db_session.query(Achievement).count() == 3

    # Re-running should not create duplicate badges.
    _unlock_achievements(db_session, student, daily_session, ts)
    db_session.commit()
    assert db_session.query(Achievement).count() == 3

    # Meet streak_7 condition later.
    student.current_streak = 7
    _unlock_achievements(db_session, student, daily_session, ts + timedelta(days=4))
    db_session.commit()
    assert db_session.query(Achievement).count() == 4


def test_create_event_validates_required_fields(db_session, seeded_students):
    try:
        import asyncio

        asyncio.run(create_event(event_data={"student_id": "jon_zhao"}, db=db_session))
        raise AssertionError("Expected HTTPException for missing fields")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "Missing fields" in str(exc.detail)


def test_update_daily_session_progress_creates_session(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    ts = datetime(2026, 2, 19, 7, 30, 0)
    session = _update_daily_session_progress(db_session, student, ts)
    db_session.commit()

    persisted = db_session.query(DailySession).filter(DailySession.id == session.id).first()
    assert persisted is not None
    assert persisted.completed_questions == 1
    assert persisted.target_questions == student.target_daily_questions
