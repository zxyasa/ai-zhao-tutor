"""9.1.1: within-group intelligent rotation (weighted random sampling)."""
from __future__ import annotations

import random
from datetime import datetime

from app.engine.adaptive import _pick_weakest_skill_in
from app.models import Mastery


def _add_mastery(db_session, student_id: str, skill_id: str, score: float, attempts: int = 50):
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


def test_weighted_sample_returns_skill_in_allowed(db_session, seeded_students):
    allowed = {"yr4_frac_equiv_001", "yr4_mult_div_001", "yr4_decimal_001"}
    _add_mastery(db_session, "jon_zhao", "yr4_frac_equiv_001", 0.5)
    _add_mastery(db_session, "jon_zhao", "yr4_mult_div_001", 0.5)
    _add_mastery(db_session, "jon_zhao", "yr4_decimal_001", 0.5)
    db_session.commit()

    rng = random.Random(0)
    picked = _pick_weakest_skill_in(db_session, "jon_zhao", allowed, rng=rng)
    assert picked in allowed


def test_weighted_sample_prefers_lower_mastery(db_session, seeded_students):
    """Over many samples, the weak skill should dominate (>=70%)."""
    allowed = {"yr4_frac_equiv_001", "yr4_mult_div_001"}
    _add_mastery(db_session, "jon_zhao", "yr4_frac_equiv_001", 0.1, attempts=50)
    _add_mastery(db_session, "jon_zhao", "yr4_mult_div_001", 0.95, attempts=50)
    db_session.commit()

    rng = random.Random(1234)
    counts = {"yr4_frac_equiv_001": 0, "yr4_mult_div_001": 0}
    for _ in range(500):
        skill = _pick_weakest_skill_in(db_session, "jon_zhao", allowed, rng=rng)
        counts[skill] += 1

    total = sum(counts.values())
    weak_share = counts["yr4_frac_equiv_001"] / total
    # (1-0.1)^2 + 0.05 = 0.86  vs  (1-0.95)^2 + 0.05 = 0.0525
    # Expected share of weak ~94%; allow generous floor for randomness.
    assert weak_share >= 0.7


def test_weighted_sample_can_still_pick_strong_skill(db_session, seeded_students):
    """Floor weight prevents starvation — even a near-mastered skill rotates in."""
    allowed = {"yr4_frac_equiv_001", "yr4_mult_div_001"}
    _add_mastery(db_session, "jon_zhao", "yr4_frac_equiv_001", 0.1)
    _add_mastery(db_session, "jon_zhao", "yr4_mult_div_001", 0.99)
    db_session.commit()

    # Deterministic rng seed that we trust will land on the small-weight bucket
    # at least once within 5000 draws (probability per draw > 0.05/(0.86+0.05)).
    rng = random.Random(42)
    seen_strong = False
    for _ in range(5000):
        if _pick_weakest_skill_in(db_session, "jon_zhao", allowed, rng=rng) == "yr4_mult_div_001":
            seen_strong = True
            break
    assert seen_strong


def test_unseen_skill_gets_weight_one(db_session, seeded_students):
    """A skill with no mastery row should still get sampled."""
    allowed = {"yr4_frac_equiv_001", "yr4_mult_div_001"}
    _add_mastery(db_session, "jon_zhao", "yr4_frac_equiv_001", 0.95)
    # yr4_mult_div_001 left without a mastery row -> weight 1.0
    db_session.commit()

    rng = random.Random(7)
    counts = {"yr4_frac_equiv_001": 0, "yr4_mult_div_001": 0}
    for _ in range(400):
        counts[_pick_weakest_skill_in(db_session, "jon_zhao", allowed, rng=rng)] += 1

    # Unseen weight 1.0 dominates the near-mastered weight 0.0525, so the
    # unseen skill should be selected the vast majority of the time.
    assert counts["yr4_mult_div_001"] > counts["yr4_frac_equiv_001"]
