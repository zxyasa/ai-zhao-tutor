from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from ..models import Achievement as DBAchievement
from ..models import DailySession as DBDailySession
from ..models import Student as DBStudent

BADGE_DEFS = {
    "streak_3": ("连续3天", "连续练习 3 天"),
    "streak_7": ("连续7天", "连续练习 7 天"),
    "daily_goal_1": ("今日达标", "首次完成每日目标"),
    "sessions_20": ("练习达人", "累计完成 20 次答题"),
}


def unlock_achievements(db: Session, student: DBStudent, daily_session: DBDailySession, now: datetime):
    maybe_grant_badge(db, student.id, "streak_3", student.current_streak >= 3, now)
    maybe_grant_badge(db, student.id, "streak_7", student.current_streak >= 7, now)
    maybe_grant_badge(db, student.id, "daily_goal_1", bool(daily_session and daily_session.is_completed), now)
    maybe_grant_badge(db, student.id, "sessions_20", student.total_sessions >= 20, now)


def maybe_grant_badge(db: Session, student_id: str, badge_key: str, condition: bool, unlocked_at: datetime):
    if not condition:
        return

    exists = db.query(DBAchievement).filter(
        DBAchievement.student_id == student_id,
        DBAchievement.badge_key == badge_key,
    ).first()
    if exists:
        return

    title, description = BADGE_DEFS[badge_key]
    db.add(
        DBAchievement(
            id=str(uuid4()),
            student_id=student_id,
            badge_key=badge_key,
            title=title,
            description=description,
            unlocked_at=unlocked_at,
        )
    )
