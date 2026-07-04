from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models.student import Base

# Create engine with SQLite fallback
engine = create_engine(
    settings.db_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.db_url else {},
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for FastAPI to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    _ensure_student_schema_compat()


def _ensure_student_schema_compat() -> None:
    """
    Keep pre-Phase8 databases forward-compatible.
    This prevents runtime 500s when older DBs miss new student columns.
    """
    statements_by_dialect = {
        "sqlite": [
            "ALTER TABLE students ADD COLUMN avatar VARCHAR DEFAULT 'star' NOT NULL",
            "ALTER TABLE students ADD COLUMN target_daily_questions INTEGER DEFAULT 10 NOT NULL",
            "ALTER TABLE students ADD COLUMN current_streak INTEGER DEFAULT 0 NOT NULL",
            "ALTER TABLE students ADD COLUMN longest_streak INTEGER DEFAULT 0 NOT NULL",
            "ALTER TABLE students ADD COLUMN last_practice_date DATE",
            "ALTER TABLE students ADD COLUMN total_sessions INTEGER DEFAULT 0 NOT NULL",
            "ALTER TABLE students ADD COLUMN parent_id VARCHAR",
            "ALTER TABLE students ADD COLUMN pin_hash VARCHAR",
            "ALTER TABLE daily_sessions ADD COLUMN bonus_questions INTEGER DEFAULT 0 NOT NULL",
            "CREATE INDEX IF NOT EXISTS ix_events_student_timestamp ON events (student_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS ix_daily_sessions_student_date ON daily_sessions (student_id, session_date DESC)",
        ],
        "postgresql": [
            "ALTER TABLE students ADD COLUMN IF NOT EXISTS avatar VARCHAR NOT NULL DEFAULT 'star'",
            "ALTER TABLE students ADD COLUMN IF NOT EXISTS target_daily_questions INTEGER NOT NULL DEFAULT 10",
            "ALTER TABLE students ADD COLUMN IF NOT EXISTS current_streak INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE students ADD COLUMN IF NOT EXISTS longest_streak INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE students ADD COLUMN IF NOT EXISTS last_practice_date DATE",
            "ALTER TABLE students ADD COLUMN IF NOT EXISTS total_sessions INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE students ADD COLUMN IF NOT EXISTS parent_id VARCHAR",
            "ALTER TABLE students ADD COLUMN IF NOT EXISTS pin_hash VARCHAR",
            "ALTER TABLE daily_sessions ADD COLUMN IF NOT EXISTS bonus_questions INTEGER NOT NULL DEFAULT 0",
            # Composite index for parent dashboard queries (student_id + timestamp range).
            # Turns the planner from single-column pick to direct composite scan;
            # matches _build_student_*_summary hot path. Cheap at 7k rows, essential at 70k+.
            "CREATE INDEX IF NOT EXISTS ix_events_student_timestamp ON events (student_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS ix_daily_sessions_student_date ON daily_sessions (student_id, session_date DESC)",
        ],
    }

    statements = statements_by_dialect.get(engine.dialect.name, [])
    if not statements:
        return

    with engine.begin() as conn:
        for statement in statements:
            try:
                conn.execute(text(statement))
            except Exception:
                # SQLite without IF NOT EXISTS may raise duplicate-column errors.
                # Safe to ignore because the target column already exists.
                if engine.dialect.name != "sqlite":
                    raise
