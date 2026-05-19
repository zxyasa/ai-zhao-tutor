from __future__ import annotations

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Event as DBEvent
from ..models import Item as DBItem
from ..models import Mastery as DBMastery
from . import progression
from .tracks import get_track_plugin


def serialize_item(item: DBItem) -> dict:
    return {
        "item_id": item.id,
        "skill_id": item.skill_id,
        "question_text": item.question_text,
        "question_type": item.question_type,
        "difficulty": item.difficulty,
        "parameters": item.parameters,
        "correct_answer": item.correct_answer,
        "hint": item.hint,
        "explanation": item.explanation,
        "validation_rule": item.validation_rule,
    }


def select_next_item(
    db: Session,
    *,
    student_id: str,
    skill_id: Optional[str] = None,
    engine_hint: Optional[str] = None,
) -> Optional[dict]:
    allowed = progression.active_skills(db, student_id)

    plugin = get_track_plugin(student_id)
    if plugin:
        item = plugin.build_item(db, allowed_skills=allowed)
        if item:
            return item

    target_skill_id = skill_id
    if target_skill_id is None and allowed:
        target_skill_id = _pick_weakest_skill_in(db, student_id, allowed)
    if target_skill_id is None:
        target_skill_id = _pick_weakest_skill(db, student_id)

    if target_skill_id:
        base_difficulty = _difficulty_from_mastery(db, student_id, target_skill_id)
        adjusted_difficulty = _apply_recent_streak_adjustment(
            db, student_id=student_id, skill_id=target_skill_id, base_difficulty=base_difficulty
        )
        adjusted_difficulty = _apply_engine_hint(adjusted_difficulty, engine_hint)

        item = _fetch_item_for_skill(db, skill_id=target_skill_id, target_difficulty=adjusted_difficulty)
        if item:
            return serialize_item(item)

    item = (
        db.query(DBItem)
        .filter(DBItem.difficulty == 1)
        .order_by(func.random())
        .first()
    )
    if item:
        return serialize_item(item)
    return None


def _pick_weakest_skill(db: Session, student_id: str) -> Optional[str]:
    weakest_skill = (
        db.query(DBMastery)
        .filter(DBMastery.student_id == student_id)
        .order_by(DBMastery.mastery_score.asc(), DBMastery.total_attempts.asc())
        .first()
    )
    if weakest_skill:
        return weakest_skill.skill_id
    return None


def _pick_weakest_skill_in(
    db: Session,
    student_id: str,
    allowed_skills: set[str],
) -> Optional[str]:
    if not allowed_skills:
        return None

    rows = (
        db.query(DBMastery)
        .filter(
            DBMastery.student_id == student_id,
            DBMastery.skill_id.in_(allowed_skills),
        )
        .all()
    )
    scores = {row.skill_id: row.mastery_score for row in rows}

    unseen = [s for s in allowed_skills if s not in scores]
    if unseen:
        return sorted(unseen)[0]

    return min(scores.items(), key=lambda kv: (kv[1], kv[0]))[0]


def _difficulty_from_mastery(db: Session, student_id: str, skill_id: str) -> int:
    mastery = (
        db.query(DBMastery)
        .filter(
            DBMastery.student_id == student_id,
            DBMastery.skill_id == skill_id,
        )
        .first()
    )
    if not mastery:
        return 1

    score = mastery.mastery_score
    if score < 0.3:
        return 1
    if score < 0.5:
        return 2
    if score < 0.7:
        return 3
    if score < 0.9:
        return 4
    return 5


def _apply_recent_streak_adjustment(
    db: Session,
    *,
    student_id: str,
    skill_id: str,
    base_difficulty: int,
) -> int:
    recent_events = (
        db.query(DBEvent.is_correct)
        .join(DBItem, DBItem.id == DBEvent.item_id)
        .filter(
            DBEvent.student_id == student_id,
            DBItem.skill_id == skill_id,
        )
        .order_by(DBEvent.timestamp.desc())
        .limit(3)
        .all()
    )
    recent_results = [row[0] for row in recent_events]

    adjustment = 0
    if len(recent_results) >= 3 and all(recent_results[:3]):
        adjustment = 1
    elif len(recent_results) >= 2 and (not recent_results[0]) and (not recent_results[1]):
        adjustment = -1

    difficulty = max(1, min(5, base_difficulty + adjustment))

    if _has_high_risk_signal(db, student_id=student_id, skill_id=skill_id):
        difficulty = max(1, difficulty - 1)

    return difficulty


def _has_high_risk_signal(db: Session, *, student_id: str, skill_id: str) -> bool:
    """
    Conservative risk trigger:
    - Last 5 attempts on a skill have low accuracy (<= 40%), or
    - Average time is very high (>= 45s), suggesting struggle.
    """
    rows = (
        db.query(DBEvent.is_correct, DBEvent.time_spent)
        .join(DBItem, DBItem.id == DBEvent.item_id)
        .filter(
            DBEvent.student_id == student_id,
            DBItem.skill_id == skill_id,
        )
        .order_by(DBEvent.timestamp.desc())
        .limit(5)
        .all()
    )
    if len(rows) < 5:
        return False

    correct_count = sum(1 for is_correct, _ in rows if is_correct)
    accuracy = correct_count / 5.0
    avg_time = sum(float(time_spent) for _, time_spent in rows) / 5.0

    return accuracy <= 0.4 or avg_time >= 45.0


def _fetch_item_for_skill(db: Session, *, skill_id: str, target_difficulty: int) -> Optional[DBItem]:
    exact = (
        db.query(DBItem)
        .filter(
            DBItem.skill_id == skill_id,
            DBItem.difficulty == target_difficulty,
        )
        .order_by(func.random())
        .first()
    )
    if exact:
        return exact

    return (
        db.query(DBItem)
        .filter(DBItem.skill_id == skill_id)
        .order_by(func.abs(DBItem.difficulty - target_difficulty), func.random())
        .first()
    )


def _apply_engine_hint(difficulty: int, engine_hint: Optional[str]) -> int:
    if not engine_hint:
        return difficulty

    hint = engine_hint.strip().lower()
    delta = 0
    if hint in {"easier", "calm"}:
        delta = -1
    elif hint == "harder":
        delta = 1
    return max(1, min(5, difficulty + delta))
