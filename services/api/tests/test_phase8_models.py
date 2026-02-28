from datetime import datetime

from app.models import Parent, Student


def test_parent_student_relationship_fields(db_session):
    parent = Parent(
        id="parent_1",
        email="parent@example.com",
        password_hash="hashed_pw",
        display_name="Parent One",
        is_active=True,
        created_at=datetime(2026, 2, 21, 10, 0, 0),
    )
    db_session.add(parent)
    db_session.commit()

    student = Student(
        id="student_1",
        name="Child One",
        year_level=4,
        avatar="lion",
        target_daily_questions=10,
        current_streak=0,
        longest_streak=0,
        total_sessions=0,
        parent_id=parent.id,
        pin_hash="hashed_pin",
        created_at=datetime(2026, 2, 21, 10, 5, 0),
    )
    db_session.add(student)
    db_session.commit()

    loaded = db_session.query(Student).filter(Student.id == "student_1").first()
    assert loaded is not None
    assert loaded.parent_id == "parent_1"
    assert loaded.pin_hash == "hashed_pin"
    assert loaded.parent is not None
    assert loaded.parent.email == "parent@example.com"
