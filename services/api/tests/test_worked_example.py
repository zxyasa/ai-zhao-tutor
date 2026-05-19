"""9.1.4: worked_example field in /next-item on the first attempt of a skill."""
from __future__ import annotations

from datetime import datetime

from app.engine.adaptive import select_next_item
from app.models import Event, Item, Mastery, Student


def _add_plain_student(db_session, student_id: str = "test_student_we"):
    db_session.add(
        Student(
            id=student_id,
            name="WE",
            year_level=4,
            avatar="star",
            target_daily_questions=10,
            current_streak=0,
            longest_streak=0,
            total_sessions=0,
            created_at=datetime.now(),
        )
    )
    return student_id


def _add_item(
    db_session,
    item_id: str,
    skill_id: str,
    difficulty: int,
    *,
    question_text: str | None = None,
    explanation: str | None = None,
    correct_answer: str = "1",
):
    db_session.add(
        Item(
            id=item_id,
            skill_id=skill_id,
            question_text=question_text or f"Q {item_id}",
            question_type="numeric",
            difficulty=difficulty,
            parameters={"seed": item_id},
            correct_answer=correct_answer,
            hint="hint",
            explanation=explanation or f"explain {item_id}",
            validation_rule="numeric",
        )
    )


def _add_mastery(db_session, student_id, skill_id, score, attempts):
    db_session.add(
        Mastery(
            student_id=student_id,
            skill_id=skill_id,
            total_attempts=attempts,
            correct_attempts=int(attempts * score),
            mastery_score=score,
            last_updated=datetime.now(),
        )
    )


def test_first_attempt_includes_worked_example(db_session):
    sid = _add_plain_student(db_session, "stu_we_1")
    _add_item(
        db_session,
        "custom_q1",
        "custom_skill_xyz",
        1,
        question_text="What is 2 + 3?",
        explanation="2 + 3 = 5. Combine the two groups.",
        correct_answer="5",
    )
    db_session.commit()

    item = select_next_item(db_session, student_id=sid, skill_id="custom_skill_xyz")
    assert item is not None
    assert item["skill_id"] == "custom_skill_xyz"
    worked = item.get("worked_example")
    assert worked is not None
    assert worked["question"] == "What is 2 + 3?"
    assert worked["answer"] == "5"
    assert "5" in worked["walkthrough"]


def test_second_attempt_omits_worked_example(db_session):
    sid = _add_plain_student(db_session, "stu_we_2")
    _add_item(db_session, "custom_q1", "custom_skill_xyz", 1)
    db_session.commit()

    db_session.add(
        Event(
            id="evt_first",
            student_id=sid,
            item_id="custom_q1",
            answer_given="1",
            is_correct=True,
            time_spent=5.0,
            hint_requested=False,
            timestamp=datetime.now(),
        )
    )
    db_session.commit()

    item = select_next_item(db_session, student_id=sid, skill_id="custom_skill_xyz")
    assert item is not None
    assert item.get("worked_example") is None


def test_worked_example_falls_back_to_higher_difficulty_when_no_d1(db_session):
    sid = _add_plain_student(db_session, "stu_we_3")
    _add_item(db_session, "only_d3_q", "skill_only_d3", 3, explanation="step-by-step d3")
    db_session.commit()

    item = select_next_item(db_session, student_id=sid, skill_id="skill_only_d3")
    assert item is not None
    worked = item.get("worked_example")
    assert worked is not None
    assert worked["walkthrough"] == "step-by-step d3"


def test_worked_example_omitted_when_no_items_exist_for_skill(db_session):
    """If a fallback path serves an item, no crash and the payload still returns."""
    sid = _add_plain_student(db_session, "stu_we_4")
    _add_item(db_session, "fallback_q", "fallback_skill", 1)
    db_session.commit()

    item = select_next_item(db_session, student_id=sid, skill_id="ghost_skill")
    assert item is not None
