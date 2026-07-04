"""baseline — snapshot of MathCoach schema on 2026-07-04

This is the canonical starting point after retrofitting Alembic on top of the
existing production database. Its `upgrade` is idempotent (`create_all` uses
IF NOT EXISTS semantics per-table via SQLAlchemy), so running it against a
pre-existing DB is safe — the intended workflow on production is:

    alembic stamp head

which marks the current state as head without executing anything.

For fresh environments (new dev machines, CI, staging):

    alembic upgrade head

builds the whole schema from the current model metadata.

Every schema change from this point on gets its own revision — no more
boot-time `ALTER TABLE IF NOT EXISTS` accumulation in database.py.

Revision ID: 2026_07_04_0001_baseline
Revises:
Create Date: 2026-07-04
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "2026_07_04_0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The models declare every table, column, index, and FK. Delegating to
    # SQLAlchemy's create_all against the current bind produces identical DDL
    # to hand-written op.create_table calls, without keeping two copies of the
    # schema in sync.
    from app.models.student import Base

    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    # Dropping every table in an app with production data would be a
    # catastrophic operation. Refuse explicitly rather than provide a
    # convenient footgun.
    raise NotImplementedError(
        "baseline down migration intentionally not implemented — restore from "
        "a database snapshot instead"
    )
