"""9.1.3: Spaced repetition.

Periodically re-test previously mastered skills so the student does not
silently lose them. A skill is considered eligible for review when:

- It clears the same mastery bar as `progression._is_skill_mastered` AND
- Its `last_updated` timestamp is at least `REVIEW_AGE_DAYS` old.

Each call to `should_inject_review` has at most `REVIEW_PROBABILITY` chance of
returning a skill_id (else None). When triggered, one eligible skill is
sampled uniformly at random.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from ..models import Mastery as DBMastery
from . import progression

REVIEW_AGE_DAYS = 7
REVIEW_PROBABILITY = 0.15


def should_inject_review(
    db: Session,
    student_id: str,
    *,
    rng: Optional[random.Random] = None,
    now: Optional[datetime] = None,
) -> Optional[str]:
    """Return a mastered-and-stale skill_id to re-test, or None.

    Most calls return None — the goal is occasional review, not constant
    interruption.
    """
    chooser = rng if rng is not None else random
    reference_time = now if now is not None else datetime.now()
    cutoff = reference_time - timedelta(days=REVIEW_AGE_DAYS)

    mastery_rows = (
        db.query(DBMastery)
        .filter(DBMastery.student_id == student_id)
        .all()
    )
    if not mastery_rows:
        return None

    mastery_by_skill = {row.skill_id: row for row in mastery_rows}
    eligible: list[str] = []
    for row in mastery_rows:
        if not progression._is_skill_mastered(row.skill_id, mastery_by_skill):
            continue
        last_updated = row.last_updated
        if last_updated is None:
            continue
        if last_updated > cutoff:
            continue
        eligible.append(row.skill_id)

    if not eligible:
        return None

    if chooser.random() >= REVIEW_PROBABILITY:
        return None

    eligible.sort()  # deterministic ordering for seeded rng tests
    return chooser.choice(eligible)
