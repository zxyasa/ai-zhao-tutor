from datetime import date, timedelta

from fastapi import HTTPException

from app.models import Student
from app.routers.students import get_streak, get_student


def test_get_streak_returns_status_fields(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    student.current_streak = 5
    student.longest_streak = 8
    student.last_practice_date = date.today() - timedelta(days=1)
    db_session.commit()

    import asyncio

    result = asyncio.run(
        get_streak("jon_zhao", db_session, claims={"role": "student", "sub": "jon_zhao"})
    )
    assert result["student_id"] == "jon_zhao"
    assert result["current_streak"] == 5
    assert result["longest_streak"] == 8
    assert result["practiced_today"] is False
    assert result["days_since_last_practice"] == 1
    assert result["is_streak_at_risk"] is True


def test_get_streak_handles_no_last_practice(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "astrid_zhao").first()
    student.current_streak = 0
    student.longest_streak = 0
    student.last_practice_date = None
    db_session.commit()

    import asyncio

    result = asyncio.run(
        get_streak("astrid_zhao", db_session, claims={"role": "student", "sub": "astrid_zhao"})
    )
    assert result["last_practice_date"] is None
    assert result["practiced_today"] is False
    assert result["days_since_last_practice"] is None
    assert result["is_streak_at_risk"] is False


def test_get_streak_student_not_found(db_session, seeded_students):
    import asyncio

    try:
        asyncio.run(
            get_streak("missing_student", db_session, claims={"role": "student", "sub": "missing_student"})
        )
        raise AssertionError("Expected HTTPException for missing student")
    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Student not found"


def test_get_student_accepts_me_alias_for_student_role(db_session, seeded_students):
    import asyncio

    result = asyncio.run(
        get_student("me", db_session, claims={"role": "student", "sub": "jon_zhao"})
    )
    assert result["id"] == "jon_zhao"
    assert result["name"] == "Jon"


def test_get_streak_accepts_me_alias_for_student_role(db_session, seeded_students):
    import asyncio

    result = asyncio.run(
        get_streak("me", db_session, claims={"role": "student", "sub": "astrid_zhao"})
    )
    assert result["student_id"] == "astrid_zhao"


def test_get_streak_me_alias_requires_explicit_student_for_parent_role(db_session, seeded_students):
    import asyncio

    try:
        asyncio.run(
            get_streak("me", db_session, claims={"role": "parent", "sub": "zhao_family"})
        )
        raise AssertionError("Expected HTTPException when parent uses me alias")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "student_id is required"
