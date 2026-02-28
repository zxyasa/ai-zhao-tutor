from datetime import datetime, timezone
from math import pow

from sqlalchemy.orm import Session

from ..models import Event as DBEvent
from ..models import Item as DBItem
from ..models import Mastery as DBMastery

MASTERY_WINDOW_SIZE = 30
HALF_LIFE_DAYS = 14.0


def compute_mastery_score_for_skill(
    db: Session,
    *,
    student_id: str,
    skill_id: str,
    reference_time: datetime,
) -> float | None:
    """
    Compute mastery using a recency-weighted window over recent events for a skill.
    More recent answers contribute higher weight.
    """
    now = _to_naive_utc(reference_time)

    recent_events = (
        db.query(DBEvent)
        .join(DBItem, DBItem.id == DBEvent.item_id)
        .filter(
            DBEvent.student_id == student_id,
            DBItem.skill_id == skill_id,
        )
        .order_by(DBEvent.timestamp.desc())
        .limit(MASTERY_WINDOW_SIZE)
        .all()
    )

    if not recent_events:
        return None

    weighted_total = 0.0
    weighted_correct = 0.0
    for event in recent_events:
        ts = _to_naive_utc(event.timestamp)
        age_days = max((now - ts).total_seconds() / 86400.0, 0.0)
        weight = pow(0.5, age_days / HALF_LIFE_DAYS)
        weighted_total += weight
        if event.is_correct:
            weighted_correct += weight

    if weighted_total <= 0:
        return None
    return weighted_correct / weighted_total


def update_mastery_for_event(
    db: Session,
    *,
    student_id: str,
    item_id: str,
    is_correct: bool,
    updated_at: datetime,
):
    # Ensure pending event insert is visible to score computation in sessions with autoflush disabled.
    db.flush()

    item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not item:
        return None

    mastery = db.query(DBMastery).filter(
        DBMastery.student_id == student_id,
        DBMastery.skill_id == item.skill_id,
    ).first()

    new_score = compute_mastery_score_for_skill(
        db,
        student_id=student_id,
        skill_id=item.skill_id,
        reference_time=updated_at,
    )

    if mastery:
        mastery.total_attempts += 1
        if is_correct:
            mastery.correct_attempts += 1
        mastery.mastery_score = new_score if new_score is not None else (mastery.correct_attempts / mastery.total_attempts)
        mastery.last_updated = updated_at
    else:
        mastery = DBMastery(
            student_id=student_id,
            skill_id=item.skill_id,
            total_attempts=1,
            correct_attempts=1 if is_correct else 0,
            mastery_score=new_score if new_score is not None else (1.0 if is_correct else 0.0),
            last_updated=updated_at,
        )
        db.add(mastery)

    return mastery


def _to_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)
