from datetime import datetime
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure `app` package is importable when running tests from services/api.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models import Achievement, DailySession, Event, Item, Mastery, Student
from app.models.student import Base


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def seeded_students(db_session):
    students = [
        Student(
            id="jon_zhao",
            name="Jon",
            year_level=4,
            avatar="lion",
            target_daily_questions=10,
            current_streak=0,
            longest_streak=0,
            total_sessions=0,
            created_at=datetime.now(),
        ),
        Student(
            id="astrid_zhao",
            name="Astrid",
            year_level=3,
            avatar="unicorn",
            target_daily_questions=10,
            current_streak=0,
            longest_streak=0,
            total_sessions=0,
            created_at=datetime.now(),
        ),
    ]
    db_session.add_all(students)
    db_session.commit()
    return students
