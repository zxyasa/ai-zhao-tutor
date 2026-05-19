from datetime import datetime, timedelta, timezone
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import hash_secret
from app.database import get_db
from app.main import app
from app.models import Event, Item, Parent, Student
from app.models.student import Base


def _seed_students(db: Session):
    db.add_all(
        [
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
    )
    db.commit()


def _build_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    setup_db = TestingSessionLocal()
    _seed_students(setup_db)
    setup_db.close()

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app), TestingSessionLocal


def _create_parent(db: Session, *, parent_id: str, email: str, password: str):
    db.add(
        Parent(
            id=parent_id,
            email=email,
            password_hash=hash_secret(password),
            display_name=email.split("@")[0],
            is_active=True,
            created_at=datetime.now(),
        )
    )
    db.commit()


def _add_item(db: Session, *, item_id: str, skill_id: str, answer: str, explanation: str):
    db.add(
        Item(
            id=item_id,
            skill_id=skill_id,
            question_text=f"Q for {item_id}",
            question_type="numeric",
            difficulty=1,
            parameters={"seed": item_id},
            correct_answer=answer,
            hint="hint",
            explanation=explanation,
            validation_rule="exact_match",
        )
    )


def _add_event(
    db: Session,
    *,
    student_id: str,
    item_id: str,
    answer: str,
    is_correct: bool,
    timestamp: datetime,
):
    db.add(
        Event(
            id=str(uuid.uuid4()),
            student_id=student_id,
            item_id=item_id,
            answer_given=answer,
            is_correct=is_correct,
            time_spent=1.0,
            hint_requested=False,
            timestamp=timestamp,
        )
    )


def _now_naive_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def test_wrong_items_returns_only_incorrect_for_student():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(db, parent_id="parent_zhao", email="zhao@example.com", password="parent-pass-123")
        student = db.query(Student).filter(Student.id == "jon_zhao").first()
        student.parent_id = "parent_zhao"
        student.pin_hash = hash_secret("1234")

        now = _now_naive_utc()
        _add_item(db, item_id="i_wrong1", skill_id="yr4_area_001", answer="42", explanation="wrong1 exp")
        _add_item(db, item_id="i_right", skill_id="yr4_area_001", answer="10", explanation="right exp")
        _add_item(db, item_id="i_wrong2", skill_id="yr4_perimeter_001", answer="3", explanation="wrong2 exp")
        _add_event(
            db,
            student_id="jon_zhao",
            item_id="i_wrong1",
            answer="41",
            is_correct=False,
            timestamp=now - timedelta(minutes=10),
        )
        _add_event(
            db,
            student_id="jon_zhao",
            item_id="i_right",
            answer="10",
            is_correct=True,
            timestamp=now - timedelta(minutes=5),
        )
        _add_event(
            db,
            student_id="jon_zhao",
            item_id="i_wrong2",
            answer="2",
            is_correct=False,
            timestamp=now - timedelta(minutes=1),
        )
        db.commit()
        db.close()

        login_resp = client.post(
            "/api/v1/auth/student-login",
            json={"student_id": "jon_zhao", "pin": "1234"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/v1/wrong-items", headers=headers)
        assert resp.status_code == 200
        payload = resp.json()
        assert isinstance(payload, list)
        assert len(payload) == 2
        # Newest first.
        assert payload[0]["item_id"] == "i_wrong2"
        assert payload[0]["your_answer"] == "2"
        assert payload[0]["correct_answer"] == "3"
        assert payload[0]["explanation"] == "wrong2 exp"
        assert payload[0]["skill_id"] == "yr4_perimeter_001"
        assert payload[1]["item_id"] == "i_wrong1"
        for entry in payload:
            assert "timestamp" in entry
            assert entry["question_text"].startswith("Q for ")
    finally:
        app.dependency_overrides.clear()


def test_wrong_items_parent_blocked_from_other_family():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(db, parent_id="parent_a", email="a@example.com", password="pass-a-123")
        _create_parent(db, parent_id="parent_b", email="b@example.com", password="pass-b-123")
        jon = db.query(Student).filter(Student.id == "jon_zhao").first()
        astrid = db.query(Student).filter(Student.id == "astrid_zhao").first()
        jon.parent_id = "parent_a"
        astrid.parent_id = "parent_b"

        now = _now_naive_utc()
        _add_item(db, item_id="i_astrid_wrong", skill_id="yr3_length_001", answer="7", explanation="exp")
        _add_event(
            db,
            student_id="astrid_zhao",
            item_id="i_astrid_wrong",
            answer="8",
            is_correct=False,
            timestamp=now - timedelta(minutes=1),
        )
        db.commit()
        db.close()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "a@example.com", "password": "pass-a-123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Missing student_id for parent: 400
        missing = client.get("/api/v1/wrong-items", headers=headers)
        assert missing.status_code == 400
        assert missing.json()["detail"] == "student_id is required"

        # Parent A cannot see Astrid (Parent B's kid): 404
        other = client.get(
            "/api/v1/wrong-items",
            params={"student_id": "astrid_zhao"},
            headers=headers,
        )
        assert other.status_code == 404
        assert other.json()["detail"] == "Student not found"

        # Parent A can see Jon (own child): empty list (no events for jon)
        own = client.get(
            "/api/v1/wrong-items",
            params={"student_id": "jon_zhao"},
            headers=headers,
        )
        assert own.status_code == 200
        assert own.json() == []
    finally:
        app.dependency_overrides.clear()


def test_wrong_items_since_today_vs_week_boundary():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(db, parent_id="parent_zhao", email="zhao@example.com", password="parent-pass-123")
        student = db.query(Student).filter(Student.id == "jon_zhao").first()
        student.parent_id = "parent_zhao"
        student.pin_hash = hash_secret("1234")

        now = _now_naive_utc()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Older than today (yesterday-ish, before midnight): 6 hours before midnight.
        before_midnight = midnight - timedelta(hours=6)
        # Within today: 1 minute after midnight (or "now" if it's still very early — pick the safer one).
        after_midnight = midnight + timedelta(minutes=1)
        if after_midnight > now:
            after_midnight = now
        # 10 days ago — outside the 7-day window.
        ten_days_ago = now - timedelta(days=10)

        _add_item(db, item_id="i_today", skill_id="yr4_area_001", answer="1", explanation="today")
        _add_item(db, item_id="i_yesterday", skill_id="yr4_area_001", answer="2", explanation="yesterday")
        _add_item(db, item_id="i_old", skill_id="yr4_area_001", answer="3", explanation="old")

        _add_event(
            db,
            student_id="jon_zhao",
            item_id="i_today",
            answer="x",
            is_correct=False,
            timestamp=after_midnight,
        )
        _add_event(
            db,
            student_id="jon_zhao",
            item_id="i_yesterday",
            answer="x",
            is_correct=False,
            timestamp=before_midnight,
        )
        _add_event(
            db,
            student_id="jon_zhao",
            item_id="i_old",
            answer="x",
            is_correct=False,
            timestamp=ten_days_ago,
        )
        db.commit()
        db.close()

        login_resp = client.post(
            "/api/v1/auth/student-login",
            json={"student_id": "jon_zhao", "pin": "1234"},
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        today_resp = client.get("/api/v1/wrong-items", headers=headers)
        assert today_resp.status_code == 200
        today_ids = {row["item_id"] for row in today_resp.json()}
        assert today_ids == {"i_today"}

        week_resp = client.get(
            "/api/v1/wrong-items", params={"since": "week"}, headers=headers
        )
        assert week_resp.status_code == 200
        week_ids = {row["item_id"] for row in week_resp.json()}
        assert week_ids == {"i_today", "i_yesterday"}

        thirty_resp = client.get(
            "/api/v1/wrong-items", params={"since": "30d"}, headers=headers
        )
        assert thirty_resp.status_code == 200
        thirty_ids = {row["item_id"] for row in thirty_resp.json()}
        assert thirty_ids == {"i_today", "i_yesterday", "i_old"}

        bad_resp = client.get(
            "/api/v1/wrong-items", params={"since": "not-a-date"}, headers=headers
        )
        assert bad_resp.status_code == 400
    finally:
        app.dependency_overrides.clear()
