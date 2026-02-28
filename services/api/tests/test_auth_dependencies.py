from fastapi import HTTPException

from app.auth.dependencies import require_student_access


def test_require_student_access_student_role_without_student_id(db_session, seeded_students):
    student = require_student_access(
        db=db_session,
        claims={"role": "student", "sub": "jon_zhao"},
        student_id=None,
    )
    assert student.id == "jon_zhao"


def test_require_student_access_parent_role_requires_student_id(db_session, seeded_students):
    try:
        require_student_access(
            db=db_session,
            claims={"role": "parent", "sub": "parent_1"},
            student_id=None,
        )
        raise AssertionError("Expected HTTPException when parent request omits student_id")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "student_id is required"


def test_require_student_access_student_role_cannot_access_other_student(db_session, seeded_students):
    try:
        require_student_access(
            db=db_session,
            claims={"role": "student", "sub": "jon_zhao"},
            student_id="astrid_zhao",
        )
        raise AssertionError("Expected HTTPException for cross-student access")
    except HTTPException as exc:
        assert exc.status_code == 403
        assert exc.detail == "Cannot access other students"
