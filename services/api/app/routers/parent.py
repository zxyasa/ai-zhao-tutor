"""Parent-facing HTTP endpoints — thin dispatchers over the analytics service.

The heavy aggregation logic lives in `services/parent_analytics_service.py`.
This file only handles:
- request validation
- auth (require_parent)
- 404 lookup for parent-owned students
- delegating to the service
- shaping the response
"""
from __future__ import annotations

import logging
import re
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth.dependencies import require_parent
from ..auth.security import hash_secret, verify_secret
from ..database import get_db
from ..models import (
    Parent as DBParent,
    ParentContextEvent as DBParentContextEvent,
    Student as DBStudent,
)
from ..services.context_ai_service import analyze_parent_context
from ..services.parent_analytics_service import (
    build_student_daily_summary,
    build_student_progress_series,
    build_student_weekly_summary,
)
from ..services.parent_notification_service import notify_parent_student_created

router = APIRouter()
logger = logging.getLogger(__name__)


class ParentContextCreate(BaseModel):
    student_id: str | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)
    free_text: str = Field(default="", max_length=1000)


class ParentStudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    year_level: int = Field(ge=1, le=12)
    pin: str = Field(min_length=4, max_length=8)
    avatar: str = Field(default="star", max_length=32)
    target_daily_questions: int = Field(default=10, ge=1, le=100)


class ParentPasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=8, max_length=256)


@router.post("/parent/context", status_code=status.HTTP_201_CREATED)
async def create_parent_context(
    payload: ParentContextCreate,
    db: Session = Depends(get_db),
    current_parent: DBParent = Depends(require_parent),
):
    student_id = payload.student_id
    if student_id:
        _get_parent_student_or_404(db, parent_id=current_parent.id, student_id=student_id)

    analysis = analyze_parent_context(tags=payload.tags, free_text=payload.free_text)
    event = DBParentContextEvent(
        parent_id=current_parent.id,
        student_id=student_id,
        free_text=payload.free_text.strip() or None,
        engine_hint=analysis.engine_hint,
        ai_insight=analysis.ai_insight,
        created_at=datetime.now(UTC),
    )
    event.tags = payload.tags
    db.add(event)
    db.commit()
    db.refresh(event)
    return {
        "id": event.id,
        "student_id": event.student_id,
        "tags": event.tags,
        "free_text": event.free_text,
        "engine_hint": event.engine_hint,
        "ai_insight": event.ai_insight,
        "created_at": event.created_at.isoformat(),
    }


@router.post("/parent/change-password")
async def change_parent_password(
    payload: ParentPasswordChangeRequest,
    db: Session = Depends(get_db),
    current_parent: DBParent = Depends(require_parent),
):
    if not verify_secret(payload.current_password, current_parent.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    new_password = payload.new_password.strip()
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    if verify_secret(new_password, current_parent.password_hash):
        raise HTTPException(status_code=400, detail="New password must be different from current password")

    current_parent.password_hash = hash_secret(new_password)
    db.add(current_parent)
    db.commit()
    return {"status": "ok"}


@router.post("/parent/students", status_code=status.HTTP_201_CREATED)
async def create_parent_student(
    payload: ParentStudentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_parent: DBParent = Depends(require_parent),
):
    pin = payload.pin.strip()
    if not pin.isdigit():
        raise HTTPException(status_code=400, detail="PIN must be numeric")

    normalized_name = payload.name.strip()
    student_id = _build_unique_student_id(db, base_name=normalized_name)
    student = DBStudent(
        id=student_id,
        name=normalized_name,
        year_level=payload.year_level,
        avatar=payload.avatar.strip() or "star",
        target_daily_questions=payload.target_daily_questions,
        current_streak=0,
        longest_streak=0,
        total_sessions=0,
        parent_id=current_parent.id,
        pin_hash=hash_secret(pin),
        created_at=datetime.now(UTC),
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # SMTP happens after response returns — a hung mail server can't stall iOS.
    background_tasks.add_task(
        _notify_and_log,
        parent_email=current_parent.email,
        student_name=student.name,
        student_id=student.id,
        initial_pin=pin,
    )
    return {
        "id": student.id,
        "name": student.name,
        "year_level": student.year_level,
        "avatar": student.avatar,
        "target_daily_questions": student.target_daily_questions,
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "last_practice_date": None,
        "total_sessions": student.total_sessions,
        "created_at": student.created_at.isoformat(),
    }


@router.get("/parent/daily-summary")
async def get_parent_daily_summary(
    db: Session = Depends(get_db),
    current_parent: DBParent = Depends(require_parent),
):
    today = date.today()
    students = (
        db.query(DBStudent)
        .filter(DBStudent.parent_id == current_parent.id)
        .order_by(DBStudent.name.asc())
        .all()
    )
    return [
        build_student_daily_summary(db, student, today, parent_id=current_parent.id)
        for student in students
    ]


@router.get("/parent/daily-summary/{student_id}")
async def get_parent_daily_summary_for_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_parent: DBParent = Depends(require_parent),
):
    student = _get_parent_student_or_404(db, parent_id=current_parent.id, student_id=student_id)
    return build_student_daily_summary(db, student, date.today(), parent_id=current_parent.id)


@router.get("/parent/weekly-summary")
async def get_parent_weekly_summary(
    db: Session = Depends(get_db),
    current_parent: DBParent = Depends(require_parent),
):
    today = date.today()
    start_day = today - timedelta(days=6)
    students = (
        db.query(DBStudent)
        .filter(DBStudent.parent_id == current_parent.id)
        .order_by(DBStudent.name.asc())
        .all()
    )
    return [
        build_student_weekly_summary(db, student, start_day, today)
        for student in students
    ]


@router.get("/parent/{student_id}/progress")
async def get_parent_student_progress(
    student_id: str,
    days: int = 30,
    db: Session = Depends(get_db),
    current_parent: DBParent = Depends(require_parent),
):
    student = _get_parent_student_or_404(db, parent_id=current_parent.id, student_id=student_id)
    window_days = max(1, min(days, 90))
    end_day = date.today()
    start_day = end_day - timedelta(days=window_days - 1)
    return build_student_progress_series(db, student, start_day, end_day)


# --- Route-scoped helpers ---------------------------------------------------


def _notify_and_log(*, parent_email: str, student_name: str, student_id: str, initial_pin: str) -> None:
    """Runs in a BackgroundTask so SMTP retries can't block the request cycle."""
    if not notify_parent_student_created(
        parent_email=parent_email,
        student_name=student_name,
        student_id=student_id,
        initial_pin=initial_pin,
    ):
        logger.warning("parent_notification_failed student_id=%s parent=%s", student_id, parent_email)


def _get_parent_student_or_404(db: Session, *, parent_id: str, student_id: str) -> DBStudent:
    student = (
        db.query(DBStudent)
        .filter(DBStudent.id == student_id, DBStudent.parent_id == parent_id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def _build_unique_student_id(db: Session, *, base_name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", base_name.lower()).strip("_")
    if not normalized:
        normalized = "student"
    candidate = normalized
    while db.query(DBStudent).filter(DBStudent.id == candidate).first():
        candidate = f"{normalized}_{uuid4().hex[:6]}"
    return candidate
