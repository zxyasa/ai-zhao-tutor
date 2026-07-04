"""Content generation helpers — deterministic IDs, dedup fingerprints.

This module is the single source of truth for how a generated item's id is
derived. It replaces the historical `uuid.uuid4().hex[:8]` pattern that made
every regeneration produce a different-looking dataset even when the underlying
questions were identical (violating CLAUDE.md's "no randomness in production"
rule).

Templates themselves don't need to import this yet — `generate_items.py`
rewrites the `item_id` field on every item post-generation, so the fix is
transparent to existing template classes. New templates should call
`deterministic_item_id(...)` directly instead of generating their own ids.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any


def deterministic_item_id(
    *,
    skill_id: str,
    difficulty: int,
    parameters: dict[str, Any],
    question_text: str,
) -> str:
    """Stable item id derived from generation inputs.

    Two runs with the same (skill_id, difficulty, parameters, question_text)
    tuple produce identical ids. This gives dedup a meaningful key and lets
    the mastery layer trust that an item id points at the same question over
    time (which the uuid-based scheme could not guarantee).

    Format: `<skill_id>_d<difficulty>_<8-char sha256>` — same shape as the
    previous scheme so downstream regex extraction of skill_id keeps working.
    """
    payload = {
        "skill": skill_id,
        "diff": int(difficulty),
        "params": _canonicalize(parameters),
        "q": question_text,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()
    return f"{skill_id}_d{difficulty}_{digest[:8]}"


def item_fingerprint(item: dict[str, Any]) -> str:
    """Dedup key — different templates producing the same question collapse."""
    return f"{item['skill_id']}|{item['difficulty']}|{item['question_text']}"


def _canonicalize(value: Any) -> Any:
    """Convert dict/list/tuple/set/other to a JSON-stable canonical form."""
    if isinstance(value, dict):
        return {k: _canonicalize(v) for k, v in sorted(value.items(), key=lambda x: str(x[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(v) for v in value]
    if isinstance(value, set):
        return sorted(_canonicalize(v) for v in value)
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    return str(value)
