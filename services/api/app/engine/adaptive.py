from __future__ import annotations

import random
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Event as DBEvent
from ..models import Item as DBItem
from ..models import Mastery as DBMastery
from . import progression, review
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
    rng: Optional[random.Random] = None,
) -> Optional[dict]:
    # 9.1.2: snapshot stage before selection so we can detect graduation.
    pre_stage_index = progression.current_stage_index(db, student_id)

    payload = _select_next_item_inner(
        db,
        student_id=student_id,
        skill_id=skill_id,
        engine_hint=engine_hint,
        rng=rng,
    )

    if payload is None:
        return None

    # 9.1.2: detect graduation that occurred as a side effect of progression
    # rules now seeing fresh mastery state. (Note: graduation truly happens
    # when mastery is updated post-event, but re-querying here keeps the
    # contract surfaced on /next-item with no extra plumbing required from
    # callers — first call AFTER graduation reports the new stage.)
    post_stage_index = progression.current_stage_index(db, student_id)
    if (
        pre_stage_index is not None
        and post_stage_index is not None
        and post_stage_index > pre_stage_index
    ):
        payload["graduated_to_index"] = post_stage_index
        payload["graduated_to_label"] = progression.stage_label(student_id, post_stage_index)

    # 9.1.4: include a worked example if this is the student's first attempt
    # on this skill.
    target_skill_id = payload.get("skill_id")
    if target_skill_id and _is_first_attempt_on_skill(db, student_id, target_skill_id):
        worked = _build_worked_example(db, target_skill_id)
        if worked is not None:
            payload["worked_example"] = worked

    return payload


def _select_next_item_inner(
    db: Session,
    *,
    student_id: str,
    skill_id: Optional[str],
    engine_hint: Optional[str],
    rng: Optional[random.Random],
) -> Optional[dict]:
    allowed = progression.active_skills(db, student_id)

    # 9.1.3: spaced-repetition review injection (only when caller did not pin
    # a specific skill_id — explicit requests still win).
    review_override: Optional[str] = None
    if skill_id is None:
        review_override = review.should_inject_review(db, student_id, rng=rng)

    plugin_allowed = allowed
    if review_override is not None:
        # Force the plugin (if any) onto the review skill if it can serve it;
        # otherwise fall through to the generic item fetch path.
        plugin_allowed = {review_override}

    plugin = get_track_plugin(student_id)
    if plugin and review_override is None:
        item = plugin.build_item(db, allowed_skills=plugin_allowed)
        if item:
            return item

    target_skill_id = skill_id
    if target_skill_id is None and review_override is not None:
        target_skill_id = review_override
    if target_skill_id is None and allowed:
        target_skill_id = _pick_weakest_skill_in(db, student_id, allowed, rng=rng)
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
    *,
    rng: Optional[random.Random] = None,
) -> Optional[str]:
    """
    9.1.1: Weighted random sample over allowed_skills.

    Lower mastery -> exponentially higher weight (squared inverse with a small
    floor so newly-mastered skills still get occasional rotations).
    Skills with no mastery row receive weight 1.0 (treated as fully unseen).
    """
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

    # Stable order so test fixtures with a seeded rng behave deterministically.
    skills = sorted(allowed_skills)
    weights: list[float] = []
    for skill in skills:
        score = scores.get(skill)
        if score is None:
            weights.append(1.0)
        else:
            clipped = min(score, 0.95)
            weights.append((1.0 - clipped) ** 2 + 0.05)

    chooser = rng if rng is not None else random
    return chooser.choices(skills, weights=weights, k=1)[0]


def _is_first_attempt_on_skill(db: Session, student_id: str, skill_id: str) -> bool:
    existing = (
        db.query(DBEvent.id)
        .join(DBItem, DBItem.id == DBEvent.item_id)
        .filter(
            DBEvent.student_id == student_id,
            DBItem.skill_id == skill_id,
        )
        .first()
    )
    return existing is None


def _build_worked_example(db: Session, skill_id: str) -> Optional[dict]:
    """9.1.4: Pick a difficulty-1 example item for the given skill, if any."""
    sample = (
        db.query(DBItem)
        .filter(DBItem.skill_id == skill_id, DBItem.difficulty == 1)
        .order_by(func.random())
        .first()
    )
    if sample is None:
        # Fallback to ANY item on the skill so worked_example can still render
        # for skills that have no difficulty-1 row (e.g. dynamic tracks where
        # an Item has not been persisted yet).
        sample = (
            db.query(DBItem)
            .filter(DBItem.skill_id == skill_id)
            .order_by(DBItem.difficulty.asc(), func.random())
            .first()
        )
    if sample is None:
        return None
    return {
        "question": sample.question_text,
        "answer": sample.correct_answer,
        "walkthrough": sample.explanation,
    }


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
