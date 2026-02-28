#!/usr/bin/env python3
import argparse
import sqlite3
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "services" / "api" / "mathcoach.db"


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def migration_files() -> list[Path]:
    return sorted(
        p for p in MIGRATIONS_DIR.glob("M-*.sql")
        if not p.name.endswith(".down.sql")
    )


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cur.fetchone() is not None


def ensure_versions_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version     TEXT PRIMARY KEY,
            applied_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        )
        """
    )
    conn.commit()


def applied_versions(conn: sqlite3.Connection) -> set[str]:
    if not table_exists(conn, "schema_migrations"):
        return set()
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def parse_version(path: Path) -> str:
    return path.name.split("__", 1)[0]


def parse_description(path: Path) -> str:
    return path.name.split("__", 1)[1].rsplit(".sql", 1)[0].replace("_", " ")


def apply_sql(conn: sqlite3.Connection, sql_path: Path) -> None:
    conn.executescript(sql_path.read_text(encoding="utf-8"))


def status(conn: sqlite3.Connection) -> None:
    if not table_exists(conn, "schema_migrations"):
        print("schema_migrations table not found")
        return

    rows = conn.execute(
        "SELECT version, applied_at, COALESCE(description, '') "
        "FROM schema_migrations ORDER BY version"
    ).fetchall()
    if not rows:
        print("schema_migrations table exists (0 applied migrations)")
        return

    print("Applied migrations:")
    for version, applied_at, description in rows:
        print(f"- {version}\t{applied_at}\t{description}")


def resolve_migrations(files: Iterable[Path], target: str | None) -> list[Path]:
    items = list(files)
    if target is None:
        return items

    matched = [p for p in items if parse_version(p) == target]
    if not matched:
        raise SystemExit(f"Migration {target} not found")
    return matched


def up(conn: sqlite3.Connection, target: str | None) -> None:
    files = resolve_migrations(migration_files(), target)
    existing = applied_versions(conn)
    if files and parse_version(files[0]) != "M-000" and not table_exists(conn, "schema_migrations"):
        raise SystemExit("schema_migrations missing. Apply M-000 first.")

    for path in files:
        version = parse_version(path)
        if version in existing:
            print(f"skip {version}: already applied")
            continue
        apply_sql(conn, path)
        if version != "M-000":
            ensure_versions_table(conn)
        conn.execute(
            "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
            (version, parse_description(path)),
        )
        conn.commit()
        print(f"applied {version}")


def down(conn: sqlite3.Connection, version: str) -> None:
    down_file = MIGRATIONS_DIR / f"{version}__init_migration_table.down.sql"
    if version != "M-000":
        matches = list(MIGRATIONS_DIR.glob(f"{version}__*.down.sql"))
        if not matches:
            raise SystemExit(f"Down migration for {version} not found")
        down_file = matches[0]

    if not down_file.exists():
        raise SystemExit(f"Down migration for {version} not found")

    apply_sql(conn, down_file)
    if table_exists(conn, "schema_migrations"):
        conn.execute("DELETE FROM schema_migrations WHERE version = ?", (version,))
        conn.commit()
    print(f"rolled back {version}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple SQLite migration runner")
    parser.add_argument("command", choices=["status", "up", "down"])
    parser.add_argument("version", nargs="?", default=None)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    with connect(db_path) as conn:
        if args.command == "status":
            status(conn)
        elif args.command == "up":
            up(conn, args.version)
        else:
            if not args.version:
                raise SystemExit("down requires a version, e.g. down M-000")
            down(conn, args.version)


if __name__ == "__main__":
    main()
