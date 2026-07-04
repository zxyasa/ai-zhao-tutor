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
    Legacy safety net for pre-Alembic SQLite dev databases.

    All schema evolution now runs through `alembic upgrade head` on production
    (see services/api/alembic/) — new columns, indices, and constraints go in
    versioned migration files, not here.

    This helper only exists so an old on-disk SQLite dev DB missing Phase 8
    columns can still boot. It is a no-op on PostgreSQL (production is fully
    managed by Alembic).
    """
    if engine.dialect.name != "sqlite":
        return

    statements = [
        "ALTER TABLE students ADD COLUMN avatar VARCHAR DEFAULT 'star' NOT NULL",
        "ALTER TABLE students ADD COLUMN target_daily_questions INTEGER DEFAULT 10 NOT NULL",
        "ALTER TABLE students ADD COLUMN current_streak INTEGER DEFAULT 0 NOT NULL",
        "ALTER TABLE students ADD COLUMN longest_streak INTEGER DEFAULT 0 NOT NULL",
        "ALTER TABLE students ADD COLUMN last_practice_date DATE",
        "ALTER TABLE students ADD COLUMN total_sessions INTEGER DEFAULT 0 NOT NULL",
        "ALTER TABLE students ADD COLUMN parent_id VARCHAR",
        "ALTER TABLE students ADD COLUMN pin_hash VARCHAR",
        "ALTER TABLE daily_sessions ADD COLUMN bonus_questions INTEGER DEFAULT 0 NOT NULL",
    ]

    with engine.begin() as conn:
        for statement in statements:
            try:
                conn.execute(text(statement))
            except Exception:
                # duplicate-column errors are expected and safe to ignore
                pass
