"""composite indices for parent dashboard hot path

The baseline migration used `Base.metadata.create_all(bind=op.get_bind())`
which respects `checkfirst=True` — on production PG the events + daily_sessions
tables already existed, so `create_all` skipped them, and the composite
indices declared in the models via `__table_args__` were never actually
created. Verified via pg_indexes after the first Alembic deploy: the indices
were missing and the query planner was still falling back to the
single-column ix_events_timestamp.

This migration creates them explicitly. Boot-time DDL (which correctly used
`CREATE INDEX IF NOT EXISTS`) was already stripped from database.py in the
Alembic retrofit commit, so this file is now the single source of truth.

Revision ID: 0002_composite_indices
Revises: 2026_07_04_0001_baseline
Create Date: 2026-07-05

Note: revision id kept short (<= 32 chars) because alembic_version.version_num
is VARCHAR(32) by default and the descriptive timestamp-prefixed style used
in the baseline maxes that out. Future revisions should stay short.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0002_composite_indices"
down_revision: Union[str, None] = "2026_07_04_0001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_events_student_timestamp",
        "events",
        ["student_id", "timestamp"],
        unique=False,
        if_not_exists=True,
    )
    op.create_index(
        "ix_daily_sessions_student_date",
        "daily_sessions",
        ["student_id", "session_date"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("ix_daily_sessions_student_date", table_name="daily_sessions")
    op.drop_index("ix_events_student_timestamp", table_name="events")
