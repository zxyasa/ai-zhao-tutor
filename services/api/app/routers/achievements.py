from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth.dependencies import get_token_claims, require_student_access
from ..database import get_db
from ..models import Achievement as DBAchievement

router = APIRouter()


def _serialize_achievement(achievement: DBAchievement) -> dict:
    return {
        "id": achievement.id,
        "student_id": achievement.student_id,
        "badge_key": achievement.badge_key,
        "title": achievement.title,
        "description": achievement.description,
        "unlocked_at": achievement.unlocked_at.isoformat(),
    }


def _resolve_since_dt(since: str | None, lookback_hours: int) -> datetime:
    if since:
        try:
            return datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid since datetime format") from exc

    bounded_hours = max(1, min(lookback_hours, 24 * 30))
    return datetime.now() - timedelta(hours=bounded_hours)


@router.get("/achievements/{student_id}")
async def get_achievements(
    student_id: str,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    resolved_id = None if student_id == "me" else student_id
    student = require_student_access(db=db, claims=claims, student_id=resolved_id)

    achievements = db.query(DBAchievement).filter(
        DBAchievement.student_id == student.id
    ).order_by(DBAchievement.unlocked_at.desc()).all()

    return [_serialize_achievement(achievement) for achievement in achievements]


@router.get("/achievements/{student_id}/new")
async def get_new_achievements(
    student_id: str,
    since: str | None = None,
    lookback_hours: int = 24,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    resolved_id = None if student_id == "me" else student_id
    student = require_student_access(db=db, claims=claims, student_id=resolved_id)
    since_dt = _resolve_since_dt(since, lookback_hours)

    new_achievements = db.query(DBAchievement).filter(
        DBAchievement.student_id == student.id,
        DBAchievement.unlocked_at >= since_dt,
    ).order_by(DBAchievement.unlocked_at.desc()).all()

    return {
        "student_id": student.id,
        "since": since_dt.isoformat(),
        "count": len(new_achievements),
        "items": [_serialize_achievement(achievement) for achievement in new_achievements],
    }


@router.get("/achievements/me")
async def get_achievements_me(
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    student = require_student_access(db=db, claims=claims, student_id=None)
    achievements = db.query(DBAchievement).filter(
        DBAchievement.student_id == student.id
    ).order_by(DBAchievement.unlocked_at.desc()).all()
    return [_serialize_achievement(achievement) for achievement in achievements]


@router.get("/achievements/me/new")
async def get_new_achievements_me(
    since: str | None = None,
    lookback_hours: int = 24,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    student = require_student_access(db=db, claims=claims, student_id=None)
    since_dt = _resolve_since_dt(since, lookback_hours)
    new_achievements = db.query(DBAchievement).filter(
        DBAchievement.student_id == student.id,
        DBAchievement.unlocked_at >= since_dt,
    ).order_by(DBAchievement.unlocked_at.desc()).all()
    return {
        "student_id": student.id,
        "since": since_dt.isoformat(),
        "count": len(new_achievements),
        "items": [_serialize_achievement(achievement) for achievement in new_achievements],
    }
