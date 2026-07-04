"""Regression tests for content generator determinism.

These lock in the CLAUDE.md rule "no randomness in production": the same
--seed must produce the same items every run, and dedup must remove
same-question collisions that used to hide behind different uuids.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make services/content/ importable when pytest collects from repo root.
CONTENT_DIR = Path(__file__).resolve().parents[1]
if str(CONTENT_DIR) not in sys.path:
    sys.path.insert(0, str(CONTENT_DIR))

from generate_items import generate_all_items
from templates.base import deterministic_item_id, item_fingerprint


def _generate(seed: int) -> list[dict]:
    return generate_all_items(seed=seed, output_path=None)


def test_same_seed_is_reproducible():
    """Two runs with seed=42 must produce identical item lists."""
    run1 = _generate(seed=42)
    run2 = _generate(seed=42)
    assert run1 == run2, "same seed must produce byte-identical items"


def test_different_seed_diverges():
    """seed=99 must produce at least some different items than seed=42."""
    run1 = _generate(seed=42)
    run99 = _generate(seed=99)
    ids1 = {item["item_id"] for item in run1}
    ids99 = {item["item_id"] for item in run99}
    assert ids1 != ids99, "different seeds should produce at least some different items"


def test_deterministic_item_id_stable():
    """Same inputs -> same id, regardless of caller context or run."""
    args = dict(
        skill_id="yr4_mult_div_001",
        difficulty=2,
        parameters={"a": 7, "b": 8},
        question_text="What is 7 × 8?",
    )
    assert deterministic_item_id(**args) == deterministic_item_id(**args)


def test_deterministic_item_id_varies_with_input():
    """Different inputs -> different ids."""
    base = dict(
        skill_id="yr4_mult_div_001",
        difficulty=2,
        parameters={"a": 7, "b": 8},
        question_text="What is 7 × 8?",
    )
    other = dict(base, parameters={"a": 8, "b": 7})
    assert deterministic_item_id(**base) != deterministic_item_id(**other)


def test_item_fingerprint_dedups_same_question():
    """Fingerprint collapses two items with same skill/difficulty/text."""
    a = {"skill_id": "s1", "difficulty": 1, "question_text": "What is 2 + 2?"}
    b = {"skill_id": "s1", "difficulty": 1, "question_text": "What is 2 + 2?"}
    assert item_fingerprint(a) == item_fingerprint(b)


def test_no_uuid_ids_in_output():
    """Every generated item id follows deterministic format, not raw uuid."""
    items = _generate(seed=42)
    for item in items[:200]:  # sample check
        item_id = item["item_id"]
        # Format is: <skill_id>_d<difficulty>_<8-hex-chars>
        skill_id = item["skill_id"]
        difficulty = item["difficulty"]
        expected_prefix = f"{skill_id}_d{difficulty}_"
        assert item_id.startswith(expected_prefix), (
            f"item_id {item_id!r} missing expected prefix {expected_prefix!r}"
        )
        suffix = item_id[len(expected_prefix):]
        assert len(suffix) == 8, f"suffix should be 8 chars of sha256, got {suffix!r}"
        assert all(c in "0123456789abcdef" for c in suffix), (
            f"suffix should be hex, got {suffix!r}"
        )
