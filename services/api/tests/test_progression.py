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


def test_jon_graduates_after_mastery(db_session, seeded_students):
    _add_mastery(db_session, "jon_zhao", "jon_carry_add_sub_100", 0.95, 200)
    for d in [1, 2, 3, 4]:
        _add_item(db_session, f"yr4_frac_equiv_d{d}", "yr4_frac_equiv_001", d)
    db_session.commit()

    item = select_next_item(db_session, student_id="jon_zhao")
    assert item is not None
    assert item["skill_id"] == "yr4_frac_equiv_001"


def test_jon_below_mastery_stays(db_session, seeded_students):
    _add_mastery(db_session, "jon_zhao", "jon_carry_add_sub_100", 0.85, 200)
    db_session.commit()

    item = select_next_item(db_session, student_id="jon_zhao")
    assert item is not None
    assert item["skill_id"] == "jon_carry_add_sub_100"


def test_jon_below_min_attempts_stays(db_session, seeded_students):
    _add_mastery(db_session, "jon_zhao", "jon_carry_add_sub_100", 0.95, 50)
    db_session.commit()

    item = select_next_item(db_session, student_id="jon_zhao")
    assert item is not None
    assert item["skill_id"] == "jon_carry_add_sub_100"


def test_astrid_filters_to_unmastered_skills(db_session, seeded_students):
    for skill in ("yr2_sem1_add_sub_100", "yr2_sem1_compare_100", "yr2_sem1_place_value"):
        _add_mastery(db_session, "astrid_zhao", skill, 1.0, 400)
    for skill in ("yr2_sem1_word_problem", "yr2_sem1_missing_number"):
        _add_mastery(db_session, "astrid_zhao", skill, 0.7, 400)
    db_session.commit()

    unmastered = {"yr2_sem1_word_problem", "yr2_sem1_missing_number"}
    for _ in range(30):
        item = select_next_item(db_session, student_id="astrid_zhao")
        assert item is not None
        assert item["skill_id"] in unmastered


def test_astrid_graduates_to_yr3(db_session, seeded_students):
    for skill in (
        "yr2_sem1_add_sub_100",
        "yr2_sem1_compare_100",
        "yr2_sem1_place_value",
        "yr2_sem1_word_problem",
        "yr2_sem1_missing_number",
    ):
        _add_mastery(db_session, "astrid_zhao", skill, 1.0, 400)
    for d in [1, 2, 3]:
        _add_item(db_session, f"yr3_frac_compare_d{d}", "yr3_frac_compare_001", d)
    db_session.commit()

    item = select_next_item(db_session, student_id="astrid_zhao")
    assert item is not None
    assert item["skill_id"] == "yr3_frac_compare_001"


def test_jon_lifetime_override_graduates(db_session, seeded_students):
    # 2000 attempts at 90% lifetime accuracy graduates even if sliding-window
    # mastery_score is below 0.9.
    _add_mastery(db_session, "jon_zhao", "jon_carry_add_sub_100", 0.86, 2000)
    for d in [1, 2, 3, 4]:
        _add_item(db_session, f"yr4_frac_equiv_d{d}", "yr4_frac_equiv_001", d)
    db_session.commit()

    item = select_next_item(db_session, student_id="jon_zhao")
    assert item is not None
    assert item["skill_id"] == "yr4_frac_equiv_001"


def test_lifetime_override_requires_min_attempts(db_session, seeded_students):
    # 500 attempts at 90% is below the 1000-attempt floor — sliding-window rules.
    _add_mastery(db_session, "jon_zhao", "jon_carry_add_sub_100", 0.86, 500)
    db_session.commit()

    item = select_next_item(db_session, student_id="jon_zhao")
    assert item is not None
    assert item["skill_id"] == "jon_carry_add_sub_100"


def test_lifetime_override_requires_min_accuracy(db_session, seeded_students):
    # 2000 attempts but lifetime accuracy 0.7 — below the 0.8 override floor.
    db_session.add(
        Mastery(
            student_id="jon_zhao",
            skill_id="jon_carry_add_sub_100",
            total_attempts=2000,
            correct_attempts=1400,
            mastery_score=0.86,
            last_updated=datetime.now(),
        )
    )
    db_session.commit()

    item = select_next_item(db_session, student_id="jon_zhao")
    assert item is not None
    assert item["skill_id"] == "jon_carry_add_sub_100"


def test_active_skills_unknown_student_returns_none(db_session):
    assert progression.active_skills(db_session, "unknown") is None


def test_active_skills_all_mastered_returns_last_group(db_session, seeded_students):
    for group in progression.SKILL_GRAPH["jon_zhao"]:
        for skill in group:
            _add_mastery(db_session, "jon_zhao", skill, 1.0, 400)
    db_session.commit()

    assert progression.active_skills(db_session, "jon_zhao") == set(
        progression.SKILL_GRAPH["jon_zhao"][-1]
    )
