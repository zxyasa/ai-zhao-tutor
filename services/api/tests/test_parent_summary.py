from datetime import date, datetime, timedelta

from app.models import Achievement, DailySession, Event, Parent, ParentContextEvent, Student
from app.routers.parent import (
    _build_student_daily_summary,
    _build_student_progress_series,
    _build_student_weekly_summary,
)


def test_daily_summary_metrics(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    student.current_streak = 3
    student.longest_streak = 5

    today = date(2026, 2, 19)
    db_session.add(
        DailySession(
            id="ds_1",
            student_id=student.id,
            session_date=today,
            started_at=datetime(2026, 2, 19, 7, 30),
            completed_questions=6,
            target_questions=10,
            is_completed=False,
            completed_at=None,
        )
    )
    db_session.add_all(
        [
            Event(
                id="e1",
                student_id=student.id,
                item_id="item_1",
                answer_given="4",
                is_correct=True,
                time_spent=8.0,
                hint_requested=False,
                timestamp=datetime(2026, 2, 19, 8, 0),
            ),
            Event(
                id="e2",
                student_id=student.id,
                item_id="item_2",
                answer_given="5",
                is_correct=False,
                time_spent=12.0,
                hint_requested=True,
                timestamp=datetime(2026, 2, 19, 8, 2),
            ),
        ]
    )
    db_session.add(
        Achievement(
            id="a1",
            student_id=student.id,
            badge_key="streak_3",
            title="连续3天",
            description="连续练习 3 天",
            unlocked_at=datetime(2026, 2, 19, 8, 5),
        )
    )
    db_session.commit()

    summary = _build_student_daily_summary(db_session, student, today)
    assert summary["completed_questions"] == 6
    assert summary["target_questions"] == 10
    assert summary["events_total"] == 2
    assert summary["correct_answers"] == 1
    assert summary["accuracy_percent"] == 50.0
    assert summary["average_time_spent_seconds"] == 10.0
    assert summary["badge_count"] == 1
    assert summary["current_streak"] == 3


def test_weekly_summary_metrics(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    student.current_streak = 4
    student.longest_streak = 6

    start_day = date(2026, 2, 13)
    end_day = date(2026, 2, 19)

    # 3 sessions, 2 completed.
    db_session.add_all(
        [
            DailySession(
                id="wds_1",
                student_id=student.id,
                session_date=start_day,
                started_at=datetime(2026, 2, 13, 7, 30),
                completed_questions=10,
                target_questions=10,
                is_completed=True,
                completed_at=datetime(2026, 2, 13, 8, 0),
            ),
            DailySession(
                id="wds_2",
                student_id=student.id,
                session_date=start_day + timedelta(days=2),
                started_at=datetime(2026, 2, 15, 7, 30),
                completed_questions=7,
                target_questions=10,
                is_completed=False,
                completed_at=None,
            ),
            DailySession(
                id="wds_3",
                student_id=student.id,
                session_date=end_day,
                started_at=datetime(2026, 2, 19, 7, 30),
                completed_questions=10,
                target_questions=10,
                is_completed=True,
                completed_at=datetime(2026, 2, 19, 8, 1),
            ),
        ]
    )
    db_session.add_all(
        [
            Event(
                id="we1",
                student_id=student.id,
                item_id="item_1",
                answer_given="1",
                is_correct=True,
                time_spent=6.0,
                hint_requested=False,
                timestamp=datetime(2026, 2, 13, 8, 0),
            ),
            Event(
                id="we2",
                student_id=student.id,
                item_id="item_2",
                answer_given="2",
                is_correct=True,
                time_spent=9.0,
                hint_requested=False,
                timestamp=datetime(2026, 2, 15, 8, 0),
            ),
            Event(
                id="we3",
                student_id=student.id,
                item_id="item_3",
                answer_given="3",
                is_correct=False,
                time_spent=14.0,
                hint_requested=True,
                timestamp=datetime(2026, 2, 19, 8, 0),
            ),
        ]
    )
    db_session.commit()

    summary = _build_student_weekly_summary(db_session, student, start_day, end_day)
    assert summary["completed_days"] == 2
    assert summary["total_completed_questions"] == 27
    assert summary["total_events"] == 3
    assert summary["accuracy_percent"] == 66.7
    assert summary["current_streak"] == 4
    assert summary["longest_streak"] == 6


def test_progress_series_metrics(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "astrid_zhao").first()
    student.current_streak = 2
    student.longest_streak = 4

    start_day = date(2026, 2, 17)
    end_day = date(2026, 2, 19)

    db_session.add_all(
        [
            DailySession(
                id="pds_1",
                student_id=student.id,
                session_date=date(2026, 2, 18),
                started_at=datetime(2026, 2, 18, 7, 30),
                completed_questions=5,
                target_questions=10,
                is_completed=False,
                completed_at=None,
            ),
            DailySession(
                id="pds_2",
                student_id=student.id,
                session_date=date(2026, 2, 19),
                started_at=datetime(2026, 2, 19, 7, 30),
                completed_questions=10,
                target_questions=10,
                is_completed=True,
                completed_at=datetime(2026, 2, 19, 8, 0),
            ),
        ]
    )
    db_session.add_all(
        [
            Event(
                id="pe1",
                student_id=student.id,
                item_id="item_11",
                answer_given="1",
                is_correct=True,
                time_spent=7.0,
                hint_requested=False,
                timestamp=datetime(2026, 2, 19, 8, 1),
            ),
            Event(
                id="pe2",
                student_id=student.id,
                item_id="item_12",
                answer_given="2",
                is_correct=False,
                time_spent=9.0,
                hint_requested=True,
                timestamp=datetime(2026, 2, 19, 8, 2),
            ),
        ]
    )
    db_session.commit()

    summary = _build_student_progress_series(db_session, student, start_day, end_day)
    assert summary["student_id"] == "astrid_zhao"
    assert summary["days"] == 3
    assert summary["current_streak"] == 2
    assert summary["longest_streak"] == 4
    assert summary["from_date"] == "2026-02-17"
    assert summary["to_date"] == "2026-02-19"
    assert summary["risk_level"] == "low"
    assert summary["risk_score"] == 0
    assert summary["risk_reasons"] == []
    assert summary["completion_rate_percent"] == 33.3
    assert summary["accuracy_volatility"] == 0.0
    assert summary["recovery_speed_days"] is None

    day_1, day_2, day_3 = summary["timeline"]
    assert day_1["date"] == "2026-02-17"
    assert day_1["events_total"] == 0
    assert day_1["completed_questions"] == 0

    assert day_2["date"] == "2026-02-18"
    assert day_2["completed_questions"] == 5
    assert day_2["target_questions"] == 10
    assert day_2["is_completed"] is False

    assert day_3["date"] == "2026-02-19"
    assert day_3["events_total"] == 2
    assert day_3["correct_answers"] == 1
    assert day_3["accuracy_percent"] == 50.0
    assert day_3["average_time_spent_seconds"] == 8.0
    assert day_3["is_completed"] is True


def test_progress_series_high_risk_signal(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()

    start_day = date(2026, 2, 13)
    end_day = date(2026, 2, 19)

    # 7 recent events, last 3 consecutive wrong, overall low accuracy.
    events = []
    for idx, is_correct in enumerate([True, False, False, True, False, False, False]):
        events.append(
            Event(
                id=f"risk_e{idx}",
                student_id=student.id,
                item_id=f"risk_item_{idx}",
                answer_given="1" if is_correct else "0",
                is_correct=is_correct,
                time_spent=50.0,
                hint_requested=False,
                timestamp=datetime(2026, 2, 13 + idx, 8, 0),
            )
        )
    db_session.add_all(events)
    db_session.commit()

    summary = _build_student_progress_series(db_session, student, start_day, end_day)
    assert summary["risk_level"] == "high"
    assert summary["risk_score"] >= 3
    assert "low_recent_accuracy" in summary["risk_reasons"]
    assert "consecutive_wrong_answers" in summary["risk_reasons"]
    assert "completion_rate_percent" in summary
    assert "accuracy_volatility" in summary
    assert "recovery_speed_days" in summary


def test_progress_series_recovery_speed_metric(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    start_day = date(2026, 2, 10)
    end_day = date(2026, 2, 13)

    db_session.add_all(
        [
            DailySession(
                id="rds_1",
                student_id=student.id,
                session_date=date(2026, 2, 10),
                started_at=datetime(2026, 2, 10, 7, 30),
                completed_questions=4,
                target_questions=10,
                is_completed=False,
                completed_at=None,
            ),
            DailySession(
                id="rds_2",
                student_id=student.id,
                session_date=date(2026, 2, 11),
                started_at=datetime(2026, 2, 11, 7, 30),
                completed_questions=6,
                target_questions=10,
                is_completed=False,
                completed_at=None,
            ),
            DailySession(
                id="rds_3",
                student_id=student.id,
                session_date=date(2026, 2, 12),
                started_at=datetime(2026, 2, 12, 7, 30),
                completed_questions=10,
                target_questions=10,
                is_completed=True,
                completed_at=datetime(2026, 2, 12, 8, 0),
            ),
        ]
    )
    db_session.add_all(
        [
            Event(
                id="re1",
                student_id=student.id,
                item_id="re_item_1",
                answer_given="0",
                is_correct=False,
                time_spent=20.0,
                hint_requested=False,
                timestamp=datetime(2026, 2, 10, 8, 0),
            ),
            Event(
                id="re2",
                student_id=student.id,
                item_id="re_item_2",
                answer_given="1",
                is_correct=True,
                time_spent=18.0,
                hint_requested=False,
                timestamp=datetime(2026, 2, 11, 8, 0),
            ),
            Event(
                id="re3",
                student_id=student.id,
                item_id="re_item_3",
                answer_given="2",
                is_correct=True,
                time_spent=17.0,
                hint_requested=False,
                timestamp=datetime(2026, 2, 11, 8, 2),
            ),
            Event(
                id="re4",
                student_id=student.id,
                item_id="re_item_4",
                answer_given="3",
                is_correct=True,
                time_spent=16.0,
                hint_requested=False,
                timestamp=datetime(2026, 2, 12, 8, 0),
            ),
        ]
    )
    db_session.commit()

    summary = _build_student_progress_series(db_session, student, start_day, end_day)
    assert summary["completion_rate_percent"] == 25.0
    assert summary["recovery_speed_days"] == 1


def test_daily_summary_has_ai_insight(db_session, seeded_students):
    student = db_session.query(Student).filter(Student.id == "jon_zhao").first()
    parent = Parent(
        id="parent_ai_1",
        email="parent-ai@example.com",
        password_hash="pbkdf2_sha256$dummy$hash",
        display_name="Parent AI",
        is_active=True,
        created_at=datetime(2026, 2, 21, 7, 0, 0),
    )
    student.parent_id = parent.id
    db_session.add(parent)
    db_session.add(
        ParentContextEvent(
            id="ctx_1",
            parent_id=parent.id,
            student_id=student.id,
            tags_json='["tired"]',
            free_text="今天比较累",
            engine_hint="easier",
            ai_insight="建议先降低难度并缩短单题时长。",
            created_at=datetime(2026, 2, 21, 7, 30, 0),
        )
    )
    db_session.commit()

    summary = _build_student_daily_summary(db_session, student, date(2026, 2, 21), parent_id=parent.id)
    assert "ai_insight" in summary
    assert "降低难度" in (summary["ai_insight"] or "")
