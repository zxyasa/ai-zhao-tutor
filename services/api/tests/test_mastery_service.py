from datetime import datetime, timedelta

from app.models import Event, Item, Mastery
from app.services.mastery_service import (
    compute_mastery_score_for_skill,
    update_mastery_for_event,
)


def test_compute_mastery_score_weights_recent_events_more(db_session, seeded_students):
    db_session.add(
        Item(
            id="item_skill_a",
            skill_id="skill_a",
            question_text="Q",
            question_type="numeric",
            difficulty=1,
            parameters={},
            correct_answer="1",
            hint="h",
            explanation="e",
            validation_rule="numeric",
        )
    )
    old_time = datetime.now() - timedelta(days=30)
    now = datetime.now()

    db_session.add_all(
        [
            Event(
                id="evt_old_correct",
                student_id="jon_zhao",
                item_id="item_skill_a",
                answer_given="1",
                is_correct=True,
                time_spent=5.0,
                hint_requested=False,
                timestamp=old_time,
            ),
            Event(
                id="evt_new_wrong",
                student_id="jon_zhao",
                item_id="item_skill_a",
                answer_given="0",
                is_correct=False,
                time_spent=5.0,
                hint_requested=False,
                timestamp=now,
            ),
        ]
    )
    db_session.commit()

    score = compute_mastery_score_for_skill(
        db_session,
        student_id="jon_zhao",
        skill_id="skill_a",
        reference_time=now,
    )

    assert score is not None
    assert score < 0.5


def test_update_mastery_for_event_uses_decayed_window_score(db_session, seeded_students):
    db_session.add(
        Item(
            id="item_skill_b",
            skill_id="skill_b",
            question_text="Q",
            question_type="numeric",
            difficulty=1,
            parameters={},
            correct_answer="1",
            hint="h",
            explanation="e",
            validation_rule="numeric",
        )
    )
    db_session.commit()

    old_time = datetime.now() - timedelta(days=20)
    new_time = datetime.now()

    # First event: old correct
    db_session.add(
        Event(
            id="evt_b_old_correct",
            student_id="astrid_zhao",
            item_id="item_skill_b",
            answer_given="1",
            is_correct=True,
            time_spent=6.0,
            hint_requested=False,
            timestamp=old_time,
        )
    )
    update_mastery_for_event(
        db_session,
        student_id="astrid_zhao",
        item_id="item_skill_b",
        is_correct=True,
        updated_at=old_time,
    )
    db_session.commit()

    # Second event: recent wrong
    db_session.add(
        Event(
            id="evt_b_new_wrong",
            student_id="astrid_zhao",
            item_id="item_skill_b",
            answer_given="0",
            is_correct=False,
            time_spent=6.0,
            hint_requested=False,
            timestamp=new_time,
        )
    )
    mastery = update_mastery_for_event(
        db_session,
        student_id="astrid_zhao",
        item_id="item_skill_b",
        is_correct=False,
        updated_at=new_time,
    )
    db_session.commit()

    assert mastery is not None
    persisted = db_session.query(Mastery).filter(
        Mastery.student_id == "astrid_zhao",
        Mastery.skill_id == "skill_b",
    ).first()

    assert persisted is not None
    assert persisted.total_attempts == 2
    assert persisted.correct_attempts == 1
    assert persisted.mastery_score < 0.5
