from datetime import UTC
import json
import logging
from datetime import date, datetime, time, timedelta
from math import sqrt
import re
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..auth.security import hash_secret, verify_secret
from ..auth.dependencies import require_parent
from ..database import get_db
from ..models import (
    Achievement as DBAchievement,
    DailySession as DBDailySession,
    Event as DBEvent,
    Parent as DBParent,
    ParentContextEvent as DBParentContextEvent,
    Student as DBStudent,
)
from ..services.context_ai_service import analyze_parent_context
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
    notify_ok = notify_parent_student_created(
        parent_email=current_parent.email,
        student_name=student.name,
        student_id=student.id,
        initial_pin=pin,
    )
    if not notify_ok:
        logger.warning("parent_notification_failed student_id=%s parent=%s", student.id, current_parent.email)
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
    students = db.query(DBStudent).filter(DBStudent.parent_id == current_parent.id).order_by(DBStudent.name.asc()).all()
    return [_build_student_daily_summary(db, student, today, parent_id=current_parent.id) for student in students]


@router.get("/parent/daily-summary/{student_id}")
async def get_parent_daily_summary_for_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_parent: DBParent = Depends(require_parent),
):
    student = _get_parent_student_or_404(db, parent_id=current_parent.id, student_id=student_id)
    return _build_student_daily_summary(db, student, date.today(), parent_id=current_parent.id)


@router.get("/parent/weekly-summary")
async def get_parent_weekly_summary(
    db: Session = Depends(get_db),
    current_parent: DBParent = Depends(require_parent),
):
    today = date.today()
    start_day = today - timedelta(days=6)

    students = db.query(DBStudent).filter(DBStudent.parent_id == current_parent.id).order_by(DBStudent.name.asc()).all()
    return [_build_student_weekly_summary(db, student, start_day, today) for student in students]


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
    return _build_student_progress_series(db, student, start_day, end_day)


def _get_parent_student_or_404(db: Session, *, parent_id: str, student_id: str) -> DBStudent:
    student = db.query(DBStudent).filter(
        DBStudent.id == student_id,
        DBStudent.parent_id == parent_id,
    ).first()
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


def _build_student_daily_summary(db: Session, student: DBStudent, day: date, parent_id: str | None = None) -> dict:
    start_dt = datetime.combine(day, time.min)
    end_dt = datetime.combine(day, time.max)

    events = db.query(DBEvent).filter(
        DBEvent.student_id == student.id,
        DBEvent.timestamp >= start_dt,
        DBEvent.timestamp <= end_dt,
    ).all()

    correct_count = sum(1 for event in events if event.is_correct)
    total_count = len(events)
    accuracy = round((correct_count / total_count) * 100, 1) if total_count else 0.0
    avg_time = round(sum(event.time_spent for event in events) / total_count, 2) if total_count else 0.0

    session = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date == day,
    ).first()

    completed_questions = session.completed_questions if session else 0
    target_questions = session.target_questions if session else student.target_daily_questions
    is_completed = session.is_completed if session else False
    badge_count = db.query(DBAchievement).filter(DBAchievement.student_id == student.id).count()
    ai_insight = _latest_ai_insight(db, parent_id=parent_id, student_id=student.id)

    return {
        "student_id": student.id,
        "student_name": student.name,
        "avatar": student.avatar,
        "session_date": day.isoformat(),
        "completed_questions": completed_questions,
        "target_questions": target_questions,
        "is_completed": is_completed,
        "events_total": total_count,
        "correct_answers": correct_count,
        "accuracy_percent": accuracy,
        "average_time_spent_seconds": avg_time,
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "badge_count": badge_count,
        "ai_insight": ai_insight,
    }


def _build_student_weekly_summary(db: Session, student: DBStudent, start_day: date, end_day: date) -> dict:
    start_dt = datetime.combine(start_day, time.min)
    end_dt = datetime.combine(end_day, time.max)

    events = db.query(DBEvent).filter(
        DBEvent.student_id == student.id,
        DBEvent.timestamp >= start_dt,
        DBEvent.timestamp <= end_dt,
    ).all()
    total_events = len(events)
    correct_events = sum(1 for event in events if event.is_correct)
    accuracy = round((correct_events / total_events) * 100, 1) if total_events else 0.0

    sessions = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date >= start_day,
        DBDailySession.session_date <= end_day,
    ).all()

    completed_days = sum(1 for session in sessions if session.is_completed)
    total_completed_questions = sum(session.completed_questions for session in sessions)

    return {
        "student_id": student.id,
        "student_name": student.name,
        "avatar": student.avatar,
        "from_date": start_day.isoformat(),
        "to_date": end_day.isoformat(),
        "completed_days": completed_days,
        "total_completed_questions": total_completed_questions,
        "total_events": total_events,
        "accuracy_percent": accuracy,
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
    }


def _build_student_progress_series(db: Session, student: DBStudent, start_day: date, end_day: date) -> dict:
    sessions = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date >= start_day,
        DBDailySession.session_date <= end_day,
    ).all()
    session_by_day = {session.session_date: session for session in sessions}

    start_dt = datetime.combine(start_day, time.min)
    end_dt = datetime.combine(end_day, time.max)
    events = db.query(DBEvent).filter(
        DBEvent.student_id == student.id,
        DBEvent.timestamp >= start_dt,
        DBEvent.timestamp <= end_dt,
    ).all()

    events_by_day = {}
    for event in events:
        day = event.timestamp.date()
        events_by_day.setdefault(day, []).append(event)

    timeline = []
    day = start_day
    while day <= end_day:
        day_events = events_by_day.get(day, [])
        total_events = len(day_events)
        correct_events = sum(1 for event in day_events if event.is_correct)
        accuracy = round((correct_events / total_events) * 100, 1) if total_events else 0.0
        avg_time = round(sum(event.time_spent for event in day_events) / total_events, 2) if total_events else 0.0

        session = session_by_day.get(day)
        completed_questions = session.completed_questions if session else 0
        target_questions = session.target_questions if session else student.target_daily_questions
        is_completed = session.is_completed if session else False

        timeline.append(
            {
                "date": day.isoformat(),
                "completed_questions": completed_questions,
                "target_questions": target_questions,
                "is_completed": is_completed,
                "events_total": total_events,
                "correct_answers": correct_events,
                "accuracy_percent": accuracy,
                "average_time_spent_seconds": avg_time,
            }
        )
        day += timedelta(days=1)

    risk = _compute_risk_signal(events)
    metrics = _compute_progress_metrics(timeline)

    return {
        "student_id": student.id,
        "student_name": student.name,
        "avatar": student.avatar,
        "from_date": start_day.isoformat(),
        "to_date": end_day.isoformat(),
        "days": len(timeline),
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "risk_level": risk["risk_level"],
        "risk_score": risk["risk_score"],
        "risk_reasons": risk["risk_reasons"],
        "completion_rate_percent": metrics["completion_rate_percent"],
        "accuracy_volatility": metrics["accuracy_volatility"],
        "recovery_speed_days": metrics["recovery_speed_days"],
        "timeline": timeline,
    }


def _compute_risk_signal(events: list[DBEvent]) -> dict:
    if not events:
        return {"risk_level": "low", "risk_score": 0, "risk_reasons": []}

    recent = sorted(events, key=lambda e: e.timestamp, reverse=True)[:7]
    total = len(recent)
    correct = sum(1 for event in recent if event.is_correct)
    accuracy = correct / total if total else 1.0
    avg_time = sum(float(event.time_spent) for event in recent) / total if total else 0.0

    consecutive_wrong = 0
    for event in recent:
        if event.is_correct:
            break
        consecutive_wrong += 1

    risk_score = 0
    reasons: list[str] = []

    if total >= 5 and accuracy <= 0.4:
        risk_score += 2
        reasons.append("low_recent_accuracy")
    if total >= 5 and avg_time >= 45.0:
        risk_score += 1
        reasons.append("high_recent_time_spent")
    if consecutive_wrong >= 3:
        risk_score += 2
        reasons.append("consecutive_wrong_answers")

    if risk_score >= 3:
        risk_level = "high"
    elif risk_score >= 1:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_reasons": reasons,
    }


def _compute_progress_metrics(timeline: list[dict]) -> dict:
    total_days = len(timeline)
    completed_days = sum(1 for day in timeline if day["is_completed"])
    completion_rate = round((completed_days / total_days) * 100, 1) if total_days else 0.0

    active_accuracies = [float(day["accuracy_percent"]) for day in timeline if day["events_total"] > 0]
    if len(active_accuracies) >= 2:
        mean = sum(active_accuracies) / len(active_accuracies)
        variance = sum((value - mean) ** 2 for value in active_accuracies) / len(active_accuracies)
        volatility = round(sqrt(variance), 2)
    else:
        volatility = 0.0

    recovery_days: int | None = None
    low_idx = None
    for idx, day in enumerate(timeline):
        if day["events_total"] > 0 and float(day["accuracy_percent"]) < 50.0:
            low_idx = idx
            break
    if low_idx is not None:
        low_date = date.fromisoformat(timeline[low_idx]["date"])
        for idx in range(low_idx + 1, len(timeline)):
            day = timeline[idx]
            if day["events_total"] > 0 and float(day["accuracy_percent"]) >= 70.0:
                recovery_date = date.fromisoformat(day["date"])
                recovery_days = (recovery_date - low_date).days
                break

    return {
        "completion_rate_percent": completion_rate,
        "accuracy_volatility": volatility,
        "recovery_speed_days": recovery_days,
    }


def _latest_ai_insight(db: Session, *, parent_id: str | None, student_id: str) -> str | None:
    if not parent_id:
        return None
    scoped = (
        db.query(DBParentContextEvent)
        .filter(
            DBParentContextEvent.parent_id == parent_id,
            DBParentContextEvent.student_id == student_id,
            DBParentContextEvent.ai_insight.isnot(None),
        )
        .order_by(DBParentContextEvent.created_at.desc())
        .first()
    )
    if scoped and scoped.ai_insight:
        return scoped.ai_insight

    general = (
        db.query(DBParentContextEvent)
        .filter(
            DBParentContextEvent.parent_id == parent_id,
            DBParentContextEvent.student_id.is_(None),
            DBParentContextEvent.ai_insight.isnot(None),
        )
        .order_by(DBParentContextEvent.created_at.desc())
        .first()
    )
    return general.ai_insight if general else None
