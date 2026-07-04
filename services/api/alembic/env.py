"""Alembic environment — reads DB URL from app config, targets Base metadata."""
from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make `app.*` importable when alembic runs from services/api/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Registers every model class against Base.metadata via the __init__.py imports.
from app.models import (  # noqa: F401 (import for side effect)
    Achievement,
    DailySession,
    Event,
    Item,
    Mastery,
    Parent,
    ParentContextEvent,
    Student,
)
from app.models.student import Base
from app.config import settings

config = context.config

# Inject the real DB URL so alembic.ini doesn't need it duplicated.
config.set_main_option("sqlalchemy.url", settings.db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
