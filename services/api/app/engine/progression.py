"""Phase 9: skill progression / auto-graduation.

Each student has an ordered list of "skill groups". The student is served only
from the first group whose skills are NOT all mastered. A skill is mastered
when mastery_score >= GRADUATION_MASTERY AND total_attempts >= GRADUATION_MIN_ATTEMPTS.
When all skills in the current group are mastered, the student graduates to
the next group automatically.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from ..models import Mastery as DBMastery

GRADUATION_MASTERY = 0.9
GRADUATION_MIN_ATTEMPTS = 100

# Lifetime override: drilled enough with decent overall accuracy = graduate,
# even if sliding-window mastery dipped below threshold.
LIFETIME_OVERRIDE_ATTEMPTS = 1000
LIFETIME_OVERRIDE_ACCURACY = 0.8

SKILL_GRAPH: dict[str, list[list[str]]] = {
    "jon_zhao": [
        ["jon_carry_add_sub_100"],
        ["yr4_frac_equiv_001"],
        ["yr5_frac_add_001"],
    ],
    "astrid_zhao": [
        [
            "yr2_sem1_add_sub_100",
            "yr2_sem1_compare_100",
            "yr2_sem1_place_value",
            "yr2_sem1_word_problem",
            "yr2_sem1_missing_number",
        ],
        ["yr3_frac_compare_001"],
        ["yr4_frac_equiv_001"],
    ],
}


def active_skills(db: Session, student_id: str) -> Optional[set[str]]:
    """Return the set of skill_ids the student should currently be served.

    Walks the student's skill groups in order. For the first group that is not
    fully mastered, returns the subset of skills within it that are not yet
    mastered. Returns None if no graph entry exists (caller falls back to old
    behavior). Returns the LAST group if all groups are mastered.
    """
    groups = SKILL_GRAPH.get(student_id)
    if not groups:
        return None

    mastery_rows = (
        db.query(DBMastery)
        .filter(DBMastery.student_id == student_id)
        .all()
    )
    mastery_by_skill = {row.skill_id: row for row in mastery_rows}

    for group in groups:
        unmastered = {s for s in group if not _is_skill_mastered(s, mastery_by_skill)}
        if unmastered:
            return unmastered

    return set(groups[-1])


def _is_skill_mastered(
    skill_id: str,
    mastery_by_skill: dict[str, DBMastery],
) -> bool:
    row = mastery_by_skill.get(skill_id)
    if row is None:
        return False
    if (
        row.total_attempts >= LIFETIME_OVERRIDE_ATTEMPTS
        and row.total_attempts > 0
        and (row.correct_attempts / row.total_attempts) >= LIFETIME_OVERRIDE_ACCURACY
    ):
        return True
    if row.mastery_score < GRADUATION_MASTERY:
        return False
    if row.total_attempts < GRADUATION_MIN_ATTEMPTS:
        return False
    return True
