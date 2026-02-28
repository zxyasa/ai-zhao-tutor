from datetime import datetime, timedelta

from fastapi import HTTPException

from app.models import Achievement
from app.routers.achievements import get_new_achievements


def test_get_new_achievements_with_default_window(db_session, seeded_students):
    now = datetime.now()
    db_session.add_all(
        [
            Achievement(
                id="a_old",
                student_id="jon_zhao",
                badge_key="old_badge",
                title="Old",
                description="old",
                unlocked_at=now - timedelta(days=3),
            ),
            Achievement(
                id="a_new",
                student_id="jon_zhao",
                badge_key="new_badge",
                title="New",
                description="new",
                unlocked_at=now - timedelta(hours=2),
            ),
        ]
    )
    db_session.commit()

    import asyncio

    payload = asyncio.run(
        get_new_achievements(
            "jon_zhao",
            db=db_session,
            claims={"role": "student", "sub": "jon_zhao"},
        )
    )
    assert payload["student_id"] == "jon_zhao"
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == "a_new"


def test_get_new_achievements_with_since_filter(db_session, seeded_students):
    db_session.add_all(
        [
            Achievement(
                id="a1",
                student_id="astrid_zhao",
                badge_key="b1",
                title="B1",
                description="d1",
                unlocked_at=datetime(2026, 2, 18, 9, 0, 0),
            ),
            Achievement(
                id="a2",
                student_id="astrid_zhao",
                badge_key="b2",
                title="B2",
                description="d2",
                unlocked_at=datetime(2026, 2, 19, 9, 0, 0),
            ),
        ]
    )
    db_session.commit()

    import asyncio

    payload = asyncio.run(
        get_new_achievements(
            "astrid_zhao",
            since="2026-02-18T12:00:00",
            db=db_session,
            claims={"role": "student", "sub": "astrid_zhao"},
        )
    )
    assert payload["count"] == 1
    assert payload["items"][0]["id"] == "a2"


def test_get_new_achievements_invalid_since(db_session, seeded_students):
    import asyncio

    try:
        asyncio.run(
            get_new_achievements(
                "jon_zhao",
                since="not-a-date",
                db=db_session,
                claims={"role": "student", "sub": "jon_zhao"},
            )
        )
        raise AssertionError("Expected HTTPException for invalid since format")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "Invalid since datetime format"


def test_get_new_achievements_student_not_found(db_session, seeded_students):
    import asyncio

    try:
        asyncio.run(
            get_new_achievements(
                "missing_student",
                db=db_session,
                claims={"role": "student", "sub": "missing_student"},
            )
        )
        raise AssertionError("Expected HTTPException for missing student")
    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Student not found"
