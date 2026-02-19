from datetime import date, datetime, timedelta

from app.models import Achievement, DailySession, Event, Student
from app.routers.parent import _build_student_daily_summary, _build_student_weekly_summary


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
