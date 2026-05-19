"""Temporary admin endpoints — used for one-off bulk content loads.

Remove this router from main.py once the corresponding load is complete.
"""
from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from ..config import settings

router = APIRouter()


class LoadItem(BaseModel):
    item_id: str
    skill_id: str
    question_text: str
    question_type: str
    difficulty: int
    parameters: dict
    correct_answer: str
    hint: str
    explanation: str
    validation_rule: str = "exact_match"


class LoadItemsRequest(BaseModel):
    items: list[LoadItem]


@router.post("/admin/load-items")
def load_items(req: LoadItemsRequest, x_admin_secret: str = Header(...)) -> dict[str, Any]:
    """Bulk insert items via raw psycopg2 with ON CONFLICT DO NOTHING.

    Only callable from inside the Railway container with the correct
    ADMIN_LOAD_SECRET. Uses the .internal Postgres endpoint via the
    container's DATABASE_URL.
    """
    expected = os.environ.get("ADMIN_LOAD_SECRET")
    if not expected or x_admin_secret != expected:
        raise HTTPException(status_code=403, detail="forbidden")

    received = len(req.items)
    if received == 0:
        return {"received": 0, "inserted": 0, "skipped": 0}

    db_url = settings.db_url
    if "postgresql" not in db_url and "postgres" not in db_url:
        raise HTTPException(status_code=500, detail="not a postgres backend")

    import json
    import psycopg2
    from psycopg2.extras import execute_values

    rows = [
        (
            it.item_id,
            it.skill_id,
            it.question_text,
            it.question_type,
            it.difficulty,
            json.dumps(it.parameters),
            it.correct_answer,
            it.hint,
            it.explanation,
            it.validation_rule,
        )
        for it in req.items
    ]

    insert_sql = (
        "INSERT INTO items "
        "(id, skill_id, question_text, question_type, difficulty, parameters, "
        "correct_answer, hint, explanation, validation_rule) "
        "VALUES %s "
        "ON CONFLICT (id) DO NOTHING"
    )

    conn = psycopg2.connect(db_url)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM items WHERE id = ANY(%s)", ([r[0] for r in rows],))
                before_existing = cur.fetchone()[0]
                execute_values(cur, insert_sql, rows, page_size=2000)
    finally:
        conn.close()

    inserted = received - before_existing
    skipped = before_existing
    return {"received": received, "inserted": inserted, "skipped": skipped}
