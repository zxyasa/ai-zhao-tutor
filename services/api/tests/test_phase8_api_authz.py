from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import hash_secret
from app.services import context_ai_service
from app.routers import parent as parent_router
from app.database import get_db
from app.main import app
from app.models import Parent, Student
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
    parent = Parent(
        id=parent_id,
        email=email,
        password_hash=hash_secret(password),
        display_name=email.split("@")[0],
        is_active=True,
        created_at=datetime.now(),
    )
    db.add(parent)
    db.commit()


def test_student_login_and_me_endpoints():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(
            db,
            parent_id="parent_zhao",
            email="zhao@example.com",
            password="parent-pass-123",
        )
        student = db.query(Student).filter(Student.id == "jon_zhao").first()
        student.parent_id = "parent_zhao"
        student.pin_hash = hash_secret("1234")
        db.commit()
        db.close()

        login_resp = client.post(
            "/api/v1/auth/student-login",
            json={"student_id": "jon_zhao", "pin": "1234"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        streak_resp = client.get("/api/v1/streak/me", headers=headers)
        assert streak_resp.status_code == 200
        assert streak_resp.json()["student_id"] == "jon_zhao"

        status_resp = client.get("/api/v1/daily-session/status", headers=headers)
        assert status_resp.status_code == 200
        assert status_resp.json()["student_id"] == "jon_zhao"
    finally:
        app.dependency_overrides.clear()


def test_student_cannot_access_other_student_scope():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(
            db,
            parent_id="parent_zhao",
            email="zhao@example.com",
            password="parent-pass-123",
        )
        student = db.query(Student).filter(Student.id == "jon_zhao").first()
        student.parent_id = "parent_zhao"
        student.pin_hash = hash_secret("1234")
        db.commit()
        db.close()

        login_resp = client.post(
            "/api/v1/auth/student-login",
            json={"student_id": "jon_zhao", "pin": "1234"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        forbidden = client.get("/api/v1/streak/astrid_zhao", headers=headers)
        assert forbidden.status_code == 403
        assert forbidden.json()["detail"] == "Cannot access other students"
    finally:
        app.dependency_overrides.clear()


def test_parent_scope_requires_student_id_and_blocks_other_family():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(db, parent_id="parent_a", email="a@example.com", password="pass-a-123")
        _create_parent(db, parent_id="parent_b", email="b@example.com", password="pass-b-123")

        jon = db.query(Student).filter(Student.id == "jon_zhao").first()
        astrid = db.query(Student).filter(Student.id == "astrid_zhao").first()
        jon.parent_id = "parent_a"
        astrid.parent_id = "parent_b"
        db.commit()
        db.close()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "a@example.com", "password": "pass-a-123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        missing_scope = client.get("/api/v1/streak/me", headers=headers)
        assert missing_scope.status_code == 400
        assert missing_scope.json()["detail"] == "student_id is required"

        own_child = client.get("/api/v1/streak/jon_zhao", headers=headers)
        assert own_child.status_code == 200
        assert own_child.json()["student_id"] == "jon_zhao"

        other_child = client.get("/api/v1/streak/astrid_zhao", headers=headers)
        assert other_child.status_code == 404
        assert other_child.json()["detail"] == "Student not found"
    finally:
        app.dependency_overrides.clear()


def test_parent_context_create_and_daily_summary_ai_insight(monkeypatch):
    monkeypatch.setattr(context_ai_service.settings, "openai_api_key", "test-key")
    monkeypatch.setattr(
        context_ai_service,
        "_call_claude_api",
        lambda **_: '{"engine_hint":"easier","ai_insight":"今天先降低难度。"}',
    )

    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(
            db,
            parent_id="parent_zhao",
            email="zhao@example.com",
            password="parent-pass-123",
        )
        student = db.query(Student).filter(Student.id == "jon_zhao").first()
        student.parent_id = "parent_zhao"
        db.commit()
        db.close()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "zhao@example.com", "password": "parent-pass-123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        context_resp = client.post(
            "/api/v1/parent/context",
            headers=headers,
            json={"student_id": "jon_zhao", "tags": ["tired"], "free_text": "状态一般"},
        )
        assert context_resp.status_code == 201
        assert context_resp.json()["engine_hint"] == "easier"

        summary_resp = client.get("/api/v1/parent/daily-summary", headers=headers)
        assert summary_resp.status_code == 200
        payload = summary_resp.json()
        assert payload[0]["student_id"] == "jon_zhao"
        assert "降低难度" in (payload[0].get("ai_insight") or "")
    finally:
        app.dependency_overrides.clear()


def test_parent_can_create_student_and_student_can_login():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(
            db,
            parent_id="parent_create",
            email="create@example.com",
            password="parent-pass-123",
        )
        db.close()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "create@example.com", "password": "parent-pass-123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        create_resp = client.post(
            "/api/v1/parent/students",
            headers=headers,
            json={
                "name": "New Kid",
                "year_level": 4,
                "pin": "4321",
                "avatar": "fox",
                "target_daily_questions": 12,
            },
        )
        assert create_resp.status_code == 201
        payload = create_resp.json()
        assert payload["name"] == "New Kid"
        assert payload["year_level"] == 4
        assert payload["target_daily_questions"] == 12
        assert payload["id"].startswith("new_kid")

        student_login_resp = client.post(
            "/api/v1/auth/student-login",
            json={"student_id": payload["id"], "pin": "4321"},
        )
        assert student_login_resp.status_code == 200
        assert student_login_resp.json()["role"] == "student"
    finally:
        app.dependency_overrides.clear()


def test_parent_change_password_success_and_old_password_rejected():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(
            db,
            parent_id="parent_pwd",
            email="pwd@example.com",
            password="old-pass-123",
        )
        db.close()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "pwd@example.com", "password": "old-pass-123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        change_resp = client.post(
            "/api/v1/parent/change-password",
            headers=headers,
            json={"current_password": "old-pass-123", "new_password": "new-pass-456"},
        )
        assert change_resp.status_code == 200
        assert change_resp.json()["status"] == "ok"

        old_login = client.post(
            "/api/v1/auth/login",
            json={"email": "pwd@example.com", "password": "old-pass-123"},
        )
        assert old_login.status_code == 401

        new_login = client.post(
            "/api/v1/auth/login",
            json={"email": "pwd@example.com", "password": "new-pass-456"},
        )
        assert new_login.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_parent_change_password_rejects_wrong_current_password():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(
            db,
            parent_id="parent_pwd_bad",
            email="pwd-bad@example.com",
            password="old-pass-123",
        )
        db.close()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "pwd-bad@example.com", "password": "old-pass-123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        change_resp = client.post(
            "/api/v1/parent/change-password",
            headers=headers,
            json={"current_password": "wrong-pass-000", "new_password": "new-pass-456"},
        )
        assert change_resp.status_code == 401
        assert change_resp.json()["detail"] == "Current password is incorrect"
    finally:
        app.dependency_overrides.clear()


def test_parent_change_password_rejects_weak_or_same_password():
    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(
            db,
            parent_id="parent_pwd_weak",
            email="pwd-weak@example.com",
            password="old-pass-123",
        )
        db.close()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "pwd-weak@example.com", "password": "old-pass-123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        weak_resp = client.post(
            "/api/v1/parent/change-password",
            headers=headers,
            json={"current_password": "old-pass-123", "new_password": "123"},
        )
        assert weak_resp.status_code == 422

        same_resp = client.post(
            "/api/v1/parent/change-password",
            headers=headers,
            json={"current_password": "old-pass-123", "new_password": "old-pass-123"},
        )
        assert same_resp.status_code == 400
        assert same_resp.json()["detail"] == "New password must be different from current password"
    finally:
        app.dependency_overrides.clear()


def test_parent_create_student_triggers_parent_notification(monkeypatch):
    called = {}

    def _fake_notify(**kwargs):
        called.update(kwargs)
        return True

    monkeypatch.setattr(parent_router, "notify_parent_student_created", _fake_notify)

    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(
            db,
            parent_id="parent_notify",
            email="notify@example.com",
            password="parent-pass-123",
        )
        db.close()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "notify@example.com", "password": "parent-pass-123"},
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        create_resp = client.post(
            "/api/v1/parent/students",
            headers=headers,
            json={"name": "Email Kid", "year_level": 4, "pin": "4321"},
        )
        assert create_resp.status_code == 201
        assert called["parent_email"] == "notify@example.com"
        assert called["student_name"] == "Email Kid"
        assert called["initial_pin"] == "4321"
    finally:
        app.dependency_overrides.clear()


def test_parent_create_student_not_blocked_when_notification_fails(monkeypatch):
    monkeypatch.setattr(parent_router, "notify_parent_student_created", lambda **kwargs: False)

    client, SessionLocal = _build_client()
    try:
        db = SessionLocal()
        _create_parent(
            db,
            parent_id="parent_notify_fail",
            email="notify-fail@example.com",
            password="parent-pass-123",
        )
        db.close()

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "notify-fail@example.com", "password": "parent-pass-123"},
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        create_resp = client.post(
            "/api/v1/parent/students",
            headers=headers,
            json={"name": "Still Created", "year_level": 4, "pin": "4321"},
        )
        assert create_resp.status_code == 201
    finally:
        app.dependency_overrides.clear()
