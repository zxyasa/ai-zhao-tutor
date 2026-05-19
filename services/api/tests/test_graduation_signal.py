"""9.1.2: graduation event detection + graduated_to fields in /next-item."""
from __future__ import annotations

from datetime import datetime

from app.engine import progression
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


def _add_mastery(db_session, student_id: str, skill_id: str, score: float, attempts: int):
    db_session.add(
        Mastery(
            student_id=student_id,
            skill_id=skill_id,
            total_attempts=attempts,
            correct_attempts=int(attempts * score),
            mastery_score=score,
            last_updated=datetime.now(),
        )
    )


def test_current_stage_index_unknown_student_returns_none(db_session):
    assert progression.current_stage_index(db_session, "unknown") is None


def test_current_stage_index_no_mastery_returns_zero(db_session, seeded_students):
    assert progression.current_stage_index(db_session, "jon_zhao") == 0


def test_current_stage_index_advances_when_first_group_mastered(db_session, seeded_students):
    _add_mastery(db_session, "jon_zhao", "jon_carry_add_sub_100", 0.95, 200)
    db_session.commit()
    assert progression.current_stage_index(db_session, "jon_zhao") == 1


def test_stage_label_returns_string(db_session, seeded_students):
    assert progression.stage_label("jon_zhao", 0) is not None
    assert "Year" in progression.stage_label("jon_zhao", 1)
    assert progression.stage_label("jon_zhao", 99) is None
    assert progression.stage_label("unknown_student", 0) is None


def test_select_next_item_reports_graduation_when_just_crossed(db_session, seeded_students):
    """
    The graduation indicator is surfaced when stage index advances between
    the pre- and post- snapshot. For this test we pre-mark Jon as mastered
    on the yr3 skill, so select_next_item will see stage_index = 1 throughout
    and pull the next-stage skill. Pre-stage uses the same query so we
    simulate a graduation by mutating mastery to a non-mastered state on
    pre-snapshot via attempts=0, then bumping to mastered before the post-snapshot.

    Simpler approach: monkey-patch current_stage_index to return 0 once
    (pre) then 1 (post).
    """
    # Add yr4 items so post-graduation pick has something to serve.
    for d in [1, 2, 3]:
        _add_item(db_session, f"yr4_frac_equiv_d{d}", "yr4_frac_equiv_001", d)
    _add_mastery(db_session, "jon_zhao", "jon_carry_add_sub_100", 0.95, 200)
    db_session.commit()

    # Patch progression.current_stage_index to fake the transition.
    call_state = {"count": 0}
    real_fn = progression.current_stage_index

    def fake(db, student_id):
        call_state["count"] += 1
        # First call (pre) returns 0; second call (post) returns the truth.
        if call_state["count"] == 1:
            return 0
        return real_fn(db, student_id)

    progression.current_stage_index = fake
    try:
        item = select_next_item(db_session, student_id="jon_zhao")
    finally:
        progression.current_stage_index = real_fn

    assert item is not None
    assert item.get("graduated_to_index") == 1
    assert item.get("graduated_to_label") is not None
    assert "Year" in item["graduated_to_label"]


def test_select_next_item_no_graduation_returns_none(db_session, seeded_students):
    """A standard call (no stage change) should leave graduated_to_* unset/None."""
    item = select_next_item(db_session, student_id="jon_zhao")
    assert item is not None
    assert item.get("graduated_to_index") is None
    assert item.get("graduated_to_label") is None
