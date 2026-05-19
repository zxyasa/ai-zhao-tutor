"""9.1.3: spaced repetition / re-test of mastered skills."""
from __future__ import annotations

import random
from datetime import datetime, timedelta

from app.engine import review
from app.engine.adaptive import select_next_item
from app.models import Item, Mastery


def _add_item(db_session, item_id: str, skill_id: str, difficulty: int):
    db_session.add(
        Item(
            id=item_id,
            skill_id=skill_id,
            question_text=f"Q {item_id}",
            question_type="numeric",
            difficulty=difficulty,
            parameters={"seed": item_id},
            correct_answer="1",
            hint="hint",
            explanation="explanation",
            validation_rule="numeric",
        )
    )


def _add_mastery(db_session, student_id, skill_id, score, attempts, last_updated):
    db_session.add(
        Mastery(
            student_id=student_id,
            skill_id=skill_id,
            total_attempts=attempts,
            correct_attempts=int(attempts * score),
            mastery_score=score,
            last_updated=last_updated,
        )
    )


def test_should_inject_review_returns_none_when_no_mastery_rows(db_session, seeded_students):
    rng = random.Random(0)
    for _ in range(50):
        assert review.should_inject_review(db_session, "jon_zhao", rng=rng) is None


def test_should_inject_review_returns_none_when_no_eligible_skills(db_session, seeded_students):
    # Mastered but updated just now -> not stale enough
    _add_mastery(
        db_session,
        "jon_zhao",
        "jon_carry_add_sub_100",
        0.95,
        200,
        datetime.now(),
    )
    db_session.commit()

    rng = random.Random(0)
    for _ in range(50):
        assert review.should_inject_review(db_session, "jon_zhao", rng=rng) is None


def test_should_inject_review_returns_none_when_not_mastered(db_session, seeded_students):
    # Old but not at mastery threshold
    _add_mastery(
        db_session,
        "jon_zhao",
        "jon_carry_add_sub_100",
        0.5,
        200,
        datetime.now() - timedelta(days=30),
    )
    db_session.commit()

    rng = random.Random(0)
    for _ in range(50):
        assert review.should_inject_review(db_session, "jon_zhao", rng=rng) is None


def test_should_inject_review_eventually_fires_for_stale_mastered_skill(db_session, seeded_students):
    _add_mastery(
        db_session,
        "jon_zhao",
        "jon_carry_add_sub_100",
        0.95,
        200,
        datetime.now() - timedelta(days=10),
    )
    db_session.commit()

    rng = random.Random(0)
    fired = False
    for _ in range(30):
        if review.should_inject_review(db_session, "jon_zhao", rng=rng) == "jon_carry_add_sub_100":
            fired = True
            break
    assert fired


def test_select_next_item_uses_review_skill_when_injected(db_session, seeded_students):
    """When the review module returns a skill, select_next_item routes to it
    (overriding both plugin and weakest-skill paths)."""
    _add_mastery(
        db_session,
        "jon_zhao",
        "jon_carry_add_sub_100",
        0.95,
        200,
        datetime.now() - timedelta(days=10),
    )
    _add_item(db_session, "review_q_d1", "review_only_skill", 1)
    db_session.commit()

    # Patch review.should_inject_review to always return our test skill_id.
    import app.engine.adaptive as adaptive_module
    real = adaptive_module.review.should_inject_review

    def fake(db, student_id, *, rng=None):
        return "review_only_skill"

    adaptive_module.review.should_inject_review = fake
    try:
        item = select_next_item(db_session, student_id="jon_zhao")
    finally:
        adaptive_module.review.should_inject_review = real

    assert item is not None
    assert item["skill_id"] == "review_only_skill"


def test_explicit_skill_id_disables_review_injection(db_session, seeded_students):
    """When the caller pins a skill_id, the review override must not fire."""
    _add_mastery(
        db_session,
        "jon_zhao",
        "jon_carry_add_sub_100",
        0.95,
        200,
        datetime.now() - timedelta(days=10),
    )
    _add_item(db_session, "explicit_q_d1", "explicit_skill", 1)
    db_session.commit()

    import app.engine.adaptive as adaptive_module
    call_count = {"n": 0}
    real = adaptive_module.review.should_inject_review

    def fake(db, student_id, *, rng=None):
        call_count["n"] += 1
        return "review_only_skill"

    adaptive_module.review.should_inject_review = fake
    try:
        item = select_next_item(db_session, student_id="jon_zhao", skill_id="explicit_skill")
    finally:
        adaptive_module.review.should_inject_review = real

    assert item is not None
    assert item["skill_id"] == "explicit_skill"
    assert call_count["n"] == 0  # review path skipped entirely
