from datetime import date, datetime

from fastapi import HTTPException

from app.models import DailySession, Student
from app.routers.daily_sessions import get_daily_session_status


def test_get_daily_session_status_accepts_me_alias_for_student_role(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    db_session.add(
        DailySession(
            id="sess_jon_today",
            student_id="jon_zhao",
            session_date=date.today(),
            started_at=datetime.now(),
            completed_questions=3,
            target_questions=student.target_daily_questions,
            is_completed=False,
            completed_at=None,
        )
    )
    db_session.commit()

    import asyncio

    result = asyncio.run(
        get_daily_session_status("me", db_session, claims={"role": "student", "sub": "jon_zhao"})
    )
    assert result["student_id"] == "jon_zhao"
    assert result["completed_questions"] == 3


def test_get_daily_session_status_me_alias_requires_explicit_student_for_parent_role(db_session, seeded_students):
    import asyncio

    try:
        asyncio.run(
            get_daily_session_status("me", db_session, claims={"role": "parent", "sub": "zhao_family"})
        )
        raise AssertionError("Expected HTTPException when parent uses me alias")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "student_id is required"
