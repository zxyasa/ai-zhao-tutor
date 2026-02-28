from datetime import datetime, timedelta

from app.engine.adaptive import select_next_item
from app.models import Event, Item, Mastery, Student


def _add_item(db_session, item_id: str, skill_id: str, difficulty: int):
    db_session.add(
        Item(
            id=item_id,
            skill_id=skill_id,
            question_text=f"Q {item_id}",
            question_type="numeric",
            difficulty=difficulty,
            parameters={"seed": item_id},
            correct_answer="1",
            hint="hint",
            explanation="explanation",
            validation_rule="numeric",
        )
    )


def test_select_next_item_prioritizes_weakest_skill(db_session, seeded_students):
    db_session.add(
        Student(
            id="student_weak",
            name="Weak",
            year_level=4,
            avatar="star",
            target_daily_questions=10,
            current_streak=0,
            longest_streak=0,
            total_sessions=0,
            created_at=datetime.now(),
        )
    )
    for difficulty in [1, 2, 3]:
        _add_item(db_session, f"weak_d{difficulty}", "skill_weak", difficulty)
        _add_item(db_session, f"strong_d{difficulty}", "skill_strong", difficulty)

    db_session.add_all(
        [
            Mastery(
                student_id="student_weak",
                skill_id="skill_weak",
                total_attempts=6,
                correct_attempts=2,
                mastery_score=0.33,
                last_updated=datetime.now(),
            ),
            Mastery(
                student_id="student_weak",
                skill_id="skill_strong",
                total_attempts=6,
                correct_attempts=6,
                mastery_score=1.0,
                last_updated=datetime.now(),
            ),
        ]
    )
    db_session.commit()

    item = select_next_item(db_session, student_id="student_weak")
    assert item is not None
    assert item["skill_id"] == "skill_weak"


def test_select_next_item_levels_up_after_three_correct(db_session, seeded_students):
    db_session.add(
        Student(
            id="student_up",
            name="Up",
            year_level=4,
            avatar="star",
            target_daily_questions=10,
            current_streak=0,
            longest_streak=0,
            total_sessions=0,
            created_at=datetime.now(),
        )
    )
    for difficulty in [2, 3, 4]:
        _add_item(db_session, f"skill_up_d{difficulty}", "skill_up", difficulty)

    db_session.add(
        Mastery(
            student_id="student_up",
            skill_id="skill_up",
            total_attempts=8,
            correct_attempts=6,
            mastery_score=0.6,  # base difficulty 3
            last_updated=datetime.now(),
        )
    )
    base_ts = datetime.now()
    for idx in range(3):
        db_session.add(
            Event(
                id=f"evt_up_{idx}",
                student_id="student_up",
                item_id="skill_up_d3",
                answer_given="1",
                is_correct=True,
                time_spent=5.0,
                hint_requested=False,
                timestamp=base_ts + timedelta(seconds=idx),
            )
        )
    db_session.commit()

    item = select_next_item(db_session, student_id="student_up", skill_id="skill_up")
    assert item is not None
    assert item["skill_id"] == "skill_up"
    assert item["difficulty"] == 4


def test_select_next_item_levels_down_after_two_wrong(db_session, seeded_students):
    db_session.add(
        Student(
            id="student_down",
            name="Down",
            year_level=4,
            avatar="star",
            target_daily_questions=10,
            current_streak=0,
            longest_streak=0,
            total_sessions=0,
            created_at=datetime.now(),
        )
    )
    for difficulty in [2, 3, 4]:
        _add_item(db_session, f"skill_down_d{difficulty}", "skill_down", difficulty)

    db_session.add(
        Mastery(
            student_id="student_down",
            skill_id="skill_down",
            total_attempts=10,
            correct_attempts=7,
            mastery_score=0.75,  # base difficulty 4
            last_updated=datetime.now(),
        )
    )
    base_ts = datetime.now()
    for idx in range(2):
        db_session.add(
            Event(
                id=f"evt_down_{idx}",
                student_id="student_down",
                item_id="skill_down_d4",
                answer_given="0",
                is_correct=False,
                time_spent=6.0,
                hint_requested=False,
                timestamp=base_ts + timedelta(seconds=idx),
            )
        )
    db_session.commit()

    item = select_next_item(db_session, student_id="student_down", skill_id="skill_down")
    assert item is not None
    assert item["skill_id"] == "skill_down"
    assert item["difficulty"] == 3


def test_select_next_item_applies_risk_penalty_on_low_recent_accuracy(db_session, seeded_students):
    db_session.add(
        Student(
            id="student_risk",
            name="Risk",
            year_level=4,
            avatar="star",
            target_daily_questions=10,
            current_streak=0,
            longest_streak=0,
            total_sessions=0,
            created_at=datetime.now(),
        )
    )
    for difficulty in [3, 4]:
        _add_item(db_session, f"skill_risk_d{difficulty}", "skill_risk", difficulty)

    db_session.add(
        Mastery(
            student_id="student_risk",
            skill_id="skill_risk",
            total_attempts=20,
            correct_attempts=15,
            mastery_score=0.75,  # base difficulty 4
            last_updated=datetime.now(),
        )
    )

    base_ts = datetime.now()
    # Pattern avoids 2-consecutive-wrong streak rule but keeps low 5-event accuracy.
    pattern = [False, True, False, True, False]
    for idx, is_correct in enumerate(pattern):
        db_session.add(
            Event(
                id=f"evt_risk_{idx}",
                student_id="student_risk",
                item_id="skill_risk_d4",
                answer_given="1" if is_correct else "0",
                is_correct=is_correct,
                time_spent=20.0,
                hint_requested=False,
                timestamp=base_ts + timedelta(seconds=idx),
            )
        )
    db_session.commit()

    item = select_next_item(db_session, student_id="student_risk", skill_id="skill_risk")
    assert item is not None
    assert item["skill_id"] == "skill_risk"
    # base 4, no streak delta, risk penalty -1 => 3
    assert item["difficulty"] == 3


def test_engine_hint_reduces_difficulty(db_session, seeded_students):
    db_session.add(
        Student(
            id="student_hint_low",
            name="Hint Low",
            year_level=4,
            avatar="star",
            target_daily_questions=10,
            current_streak=0,
            longest_streak=0,
            total_sessions=0,
            created_at=datetime.now(),
        )
    )
    for difficulty in [2, 3, 4]:
        _add_item(db_session, f"skill_hint_low_d{difficulty}", "skill_hint_low", difficulty)
    db_session.add(
        Mastery(
            student_id="student_hint_low",
            skill_id="skill_hint_low",
            total_attempts=8,
            correct_attempts=6,
            mastery_score=0.6,  # base 3
            last_updated=datetime.now(),
        )
    )
    db_session.commit()

    item = select_next_item(
        db_session,
        student_id="student_hint_low",
        skill_id="skill_hint_low",
        engine_hint="easier",
    )
    assert item is not None
    assert item["difficulty"] == 2


def test_engine_hint_none_no_effect(db_session, seeded_students):
    db_session.add(
        Student(
            id="student_hint_none",
            name="Hint None",
            year_level=4,
            avatar="star",
            target_daily_questions=10,
            current_streak=0,
            longest_streak=0,
            total_sessions=0,
            created_at=datetime.now(),
        )
    )
    for difficulty in [2, 3, 4]:
        _add_item(db_session, f"skill_hint_none_d{difficulty}", "skill_hint_none", difficulty)
    db_session.add(
        Mastery(
            student_id="student_hint_none",
            skill_id="skill_hint_none",
            total_attempts=8,
            correct_attempts=6,
            mastery_score=0.6,  # base 3
            last_updated=datetime.now(),
        )
    )
    db_session.commit()

    item = select_next_item(
        db_session,
        student_id="student_hint_none",
        skill_id="skill_hint_none",
        engine_hint=None,
    )
    assert item is not None
    assert item["difficulty"] == 3
