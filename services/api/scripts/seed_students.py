#!/usr/bin/env python3
"""
Seed canonical student profiles for local development.

Usage:
  cd services/api/scripts
  python seed_students.py
"""
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.database import SessionLocal, init_db, engine
from app.models import Student

STUDENTS = [
    {
        "id": "jon_zhao",
        "name": "Jon",
        "year_level": 4,
        "avatar": "lion",
        "target_daily_questions": 10,
    },
    {
        "id": "astrid_zhao",
        "name": "Astrid",
        "year_level": 3,
        "avatar": "unicorn",
        "target_daily_questions": 10,
    },
]


def seed_students() -> bool:
    init_db()
    db = SessionLocal()
    now = datetime.now()

    created = 0
    updated = 0

    try:
        _ensure_student_schema(db)

        for entry in STUDENTS:
            existing = db.query(Student).filter(Student.id == entry["id"]).first()
            if existing:
                existing.name = entry["name"]
                existing.year_level = entry["year_level"]
                existing.avatar = entry["avatar"]
                existing.target_daily_questions = entry["target_daily_questions"]
                updated += 1
                continue

            db.add(
                Student(
                    id=entry["id"],
                    name=entry["name"],
                    year_level=entry["year_level"],
                    avatar=entry["avatar"],
                    target_daily_questions=entry["target_daily_questions"],
                    current_streak=0,
                    longest_streak=0,
                    total_sessions=0,
                    created_at=now,
                )
            )
            created += 1

        db.commit()
        print(f"✅ Seed complete. created={created}, updated={updated}")
        for student in db.query(Student).order_by(Student.name.asc()).all():
            print(
                f"   - {student.id}: {student.name} (Year {student.year_level}, "
                f"avatar={student.avatar}, daily_target={student.target_daily_questions})"
            )
        return True
    except Exception as exc:
        db.rollback()
        print(f"❌ Failed to seed students: {exc}")
        return False
    finally:
        db.close()


def _ensure_student_schema(db) -> None:
    if engine.dialect.name != "sqlite":
        return

    existing_cols = {
        row[1]
        for row in db.execute(text("PRAGMA table_info(students)")).fetchall()
    }

    alter_statements = {
        "avatar": "ALTER TABLE students ADD COLUMN avatar VARCHAR DEFAULT 'star' NOT NULL",
        "target_daily_questions": "ALTER TABLE students ADD COLUMN target_daily_questions INTEGER DEFAULT 10 NOT NULL",
        "current_streak": "ALTER TABLE students ADD COLUMN current_streak INTEGER DEFAULT 0 NOT NULL",
        "longest_streak": "ALTER TABLE students ADD COLUMN longest_streak INTEGER DEFAULT 0 NOT NULL",
        "last_practice_date": "ALTER TABLE students ADD COLUMN last_practice_date DATE",
        "total_sessions": "ALTER TABLE students ADD COLUMN total_sessions INTEGER DEFAULT 0 NOT NULL",
    }

    for col_name, statement in alter_statements.items():
        if col_name not in existing_cols:
            db.execute(text(statement))

    db.commit()


if __name__ == "__main__":
    ok = seed_students()
    raise SystemExit(0 if ok else 1)
