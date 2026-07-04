"""Parent-facing analytics — daily/weekly summaries, progress series, risk.

Extracted from routers/parent.py so the router can be thin dispatchers and
this module owns the aggregation logic. All queries here run against the
composite indices declared in models/event.py and models/daily_session.py,
so the hot path is a single scan per student per query.

Nothing in here touches request/response objects — dicts in, dicts out —
which keeps it easy to unit-test without spinning up FastAPI.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from math import sqrt
from typing import Any

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from ..models import (
    Achievement as DBAchievement,
    DailySession as DBDailySession,
    Event as DBEvent,
    ParentContextEvent as DBParentContextEvent,
    Student as DBStudent,
)


def build_student_daily_summary(
    db: Session,
    student: DBStudent,
    day: date,
    *,
    parent_id: str | None = None,
) -> dict[str, Any]:
    """One-day snapshot: events / accuracy / session progress / streak / badges."""
    start_dt = datetime.combine(day, time.min)
    end_dt = datetime.combine(day, time.max)

    # Single-row aggregate over the composite (student_id, timestamp) index.
    agg = db.query(
        func.count(DBEvent.id).label("total"),
        func.sum(case((DBEvent.is_correct.is_(True), 1), else_=0)).label("correct"),
        func.coalesce(func.sum(DBEvent.time_spent), 0.0).label("total_time"),
    ).filter(
        DBEvent.student_id == student.id,
        DBEvent.timestamp >= start_dt,
        DBEvent.timestamp <= end_dt,
    ).one()

    total_count = int(agg.total or 0)
    correct_count = int(agg.correct or 0)
    total_time = float(agg.total_time or 0.0)
    accuracy = round((correct_count / total_count) * 100, 1) if total_count else 0.0
    avg_time = round(total_time / total_count, 2) if total_count else 0.0

    session = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date == day,
    ).first()

    completed_questions = session.completed_questions if session else 0
    target_questions = session.target_questions if session else student.target_daily_questions
    is_completed = session.is_completed if session else False
    badge_count = db.query(DBAchievement).filter(DBAchievement.student_id == student.id).count()
    ai_insight = latest_ai_insight(db, parent_id=parent_id, student_id=student.id)

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


def build_student_weekly_summary(
    db: Session,
    student: DBStudent,
    start_day: date,
    end_day: date,
) -> dict[str, Any]:
    """7-day (or arbitrary window) rollup — events + sessions in two aggregates."""
    start_dt = datetime.combine(start_day, time.min)
    end_dt = datetime.combine(end_day, time.max)

    events_agg = db.query(
        func.count(DBEvent.id).label("total"),
        func.sum(case((DBEvent.is_correct.is_(True), 1), else_=0)).label("correct"),
    ).filter(
        DBEvent.student_id == student.id,
        DBEvent.timestamp >= start_dt,
        DBEvent.timestamp <= end_dt,
    ).one()
    total_events = int(events_agg.total or 0)
    correct_events = int(events_agg.correct or 0)
    accuracy = round((correct_events / total_events) * 100, 1) if total_events else 0.0

    sessions_agg = db.query(
        func.sum(case((DBDailySession.is_completed.is_(True), 1), else_=0)).label("completed_days"),
        func.coalesce(func.sum(DBDailySession.completed_questions), 0).label("total_completed"),
    ).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date >= start_day,
        DBDailySession.session_date <= end_day,
    ).one()

    completed_days = int(sessions_agg.completed_days or 0)
    total_completed_questions = int(sessions_agg.total_completed or 0)

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


def build_student_progress_series(
    db: Session,
    student: DBStudent,
    start_day: date,
    end_day: date,
) -> dict[str, Any]:
    """Per-day timeline + risk signal + volatility metrics."""
    sessions = db.query(DBDailySession).filter(
        DBDailySession.student_id == student.id,
        DBDailySession.session_date >= start_day,
        DBDailySession.session_date <= end_day,
    ).all()
    session_by_day = {s.session_date: s for s in sessions}

    start_dt = datetime.combine(start_day, time.min)
    end_dt = datetime.combine(end_day, time.max)

    # GROUP BY day at the SQL layer — one row per day, not one row per event.
    day_col = func.date(DBEvent.timestamp).label("day")
    events_by_day_agg = db.query(
        day_col,
        func.count(DBEvent.id).label("total"),
        func.sum(case((DBEvent.is_correct.is_(True), 1), else_=0)).label("correct"),
        func.coalesce(func.sum(DBEvent.time_spent), 0.0).label("total_time"),
    ).filter(
        DBEvent.student_id == student.id,
        DBEvent.timestamp >= start_dt,
        DBEvent.timestamp <= end_dt,
    ).group_by(day_col).all()

    events_by_day = {}
    for row in events_by_day_agg:
        day_key = row.day if isinstance(row.day, date) else date.fromisoformat(str(row.day))
        events_by_day[day_key] = row

    timeline: list[dict[str, Any]] = []
    day = start_day
    while day <= end_day:
        row = events_by_day.get(day)
        total_events = int(row.total) if row else 0
        correct_events = int(row.correct) if row else 0
        total_time = float(row.total_time) if row else 0.0
        accuracy = round((correct_events / total_events) * 100, 1) if total_events else 0.0
        avg_time = round(total_time / total_events, 2) if total_events else 0.0

        session = session_by_day.get(day)
        completed_questions = session.completed_questions if session else 0
        target_questions = session.target_questions if session else student.target_daily_questions
        is_completed = session.is_completed if session else False

        timeline.append({
            "date": day.isoformat(),
            "completed_questions": completed_questions,
            "target_questions": target_questions,
            "is_completed": is_completed,
            "events_total": total_events,
            "correct_answers": correct_events,
            "accuracy_percent": accuracy,
            "average_time_spent_seconds": avg_time,
        })
        day += timedelta(days=1)

    # Risk signal only needs the 7 most-recent events in the window.
    recent_events = db.query(DBEvent).filter(
        DBEvent.student_id == student.id,
        DBEvent.timestamp >= start_dt,
        DBEvent.timestamp <= end_dt,
    ).order_by(DBEvent.timestamp.desc()).limit(7).all()

    risk = compute_risk_signal(recent_events)
    metrics = compute_progress_metrics(timeline)

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


def compute_risk_signal(events: list[DBEvent]) -> dict[str, Any]:
    """Score the last-7 slice for warning conditions the parent should notice."""
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

    return {"risk_level": risk_level, "risk_score": risk_score, "risk_reasons": reasons}


def compute_progress_metrics(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    """Volatility and recovery metrics derived from an already-built timeline."""
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
    low_idx: int | None = None
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


def latest_ai_insight(db: Session, *, parent_id: str | None, student_id: str) -> str | None:
    """Look up the latest AI insight — student-scoped first, then general."""
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
