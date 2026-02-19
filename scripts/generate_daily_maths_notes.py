#!/usr/bin/env python3
"""
Generate daily maths worksheets for Astrid and Jon, then upsert to Apple Notes.

Rules:
- Title format: "Maths - <Name> - YYYY-MM-DD"
- 40 questions each day
- No "__" suffix after "="
- Astrid: Year 2 first month, foundational
- Jon: carrying addition + borrowing subtraction within 100 only
"""

from __future__ import annotations

import datetime as dt
import html
import random
import subprocess
import tempfile
from pathlib import Path


ASTRID_FOLDER = "Astrid Maths"
JON_FOLDER = "Jon Maths"


def _build_astrid_questions(rng: random.Random) -> list[str]:
    rows: list[str] = []
    for i in range(1, 41):
        if i % 4 == 1:
            a = rng.randint(1, 9)
            b = rng.randint(1, 9)
            rows.append(f"{i}. {a} + {b} =")
        elif i % 4 == 2:
            a = rng.randint(10, 30)
            b = rng.randint(1, min(9, a - 1))
            rows.append(f"{i}. {a} - {b} =")
        elif i % 4 == 3:
            total = rng.randint(8, 30)
            take = rng.randint(1, min(10, total - 1))
            rows.append(
                f"{i}. There are {total} pencils. {take} are taken away. How many are left?"
            )
        else:
            a = rng.randint(2, 20)
            b = rng.randint(2, 20)
            rows.append(f"{i}. {a} + {b} =")
    return rows


def _build_jon_questions(rng: random.Random) -> list[str]:
    rows: list[str] = []
    for i in range(1, 41):
        if i % 2 == 1:
            # Carrying addition within 100.
            while True:
                u1 = rng.randint(5, 9)
                u2 = rng.randint(5, 9)
                t1 = rng.randint(1, 4)
                t2 = rng.randint(1, 4)
                a = t1 * 10 + u1
                b = t2 * 10 + u2
                if (u1 + u2) >= 10 and (a + b) <= 100:
                    rows.append(f"{i}. {a} + {b} =")
                    break
        else:
            # Borrowing subtraction within 100.
            while True:
                top_t = rng.randint(2, 9)
                top_u = rng.randint(0, 4)
                bot_t = rng.randint(1, top_t - 1)
                bot_u = rng.randint(top_u + 1, 9)
                a = top_t * 10 + top_u
                b = bot_t * 10 + bot_u
                d = a - b
                if top_u < bot_u and 0 <= d <= 100:
                    rows.append(f"{i}. {a} - {b} =")
                    break
    return rows


def _to_notes_html(lines: list[str]) -> str:
    escaped = [html.escape(line) for line in lines]
    return (
        '<div style="font-family: Menlo, monospace; white-space: normal;">'
        + "<br>".join(escaped)
        + "</div>"
    )


def _upsert_note(folder_name: str, note_title: str, note_html: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(note_html)
        tmp_path = f.name

    script = [
        "/usr/bin/osascript",
        "-e",
        f'set noteTitle to "{note_title}"',
        "-e",
        f'set p to POSIX file "{tmp_path}"',
        "-e",
        "set t to read p",
        "-e",
        'tell application "Notes"',
        "-e",
        f'if not (exists folder "{folder_name}") then make new folder with properties {{name:"{folder_name}"}}',
        "-e",
        f'set f to folder "{folder_name}"',
        "-e",
        "set hits to every note of f whose name is noteTitle",
        "-e",
        "if (count of hits) > 0 then",
        "-e",
        "repeat with n in hits",
        "-e",
        "set body of n to t",
        "-e",
        "set name of n to noteTitle",
        "-e",
        "end repeat",
        "-e",
        "else",
        "-e",
        "make new note at f with properties {name:noteTitle, body:t}",
        "-e",
        "end if",
        "-e",
        "end tell",
    ]
    subprocess.run(script, check=True)


def main() -> None:
    today = dt.date.today().isoformat()
    rng = random.Random(today + "-maths-daily")

    astrid_title = f"Maths - Astrid - {today}"
    jon_title = f"Maths - Jon - {today}"

    astrid_lines = _build_astrid_questions(rng)
    jon_lines = _build_jon_questions(rng)

    _upsert_note(ASTRID_FOLDER, astrid_title, _to_notes_html(astrid_lines))
    _upsert_note(JON_FOLDER, jon_title, _to_notes_html(jon_lines))


if __name__ == "__main__":
    main()

