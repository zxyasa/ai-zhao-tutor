from sqlalchemy import Column, String, Integer, DateTime, Date, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from .student import Base


class DailySession(Base):
    __tablename__ = "daily_sessions"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    session_date = Column(Date, nullable=False, index=True)
    started_at = Column(DateTime, nullable=False)
    completed_questions = Column(Integer, nullable=False, default=0)
    target_questions = Column(Integer, nullable=False, default=10)
    bonus_questions = Column(Integer, nullable=False, default=0)
    is_completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_daily_sessions_student_date", "student_id", "session_date"),
    )

    student = relationship("Student")

    def __repr__(self):
        return (
            f"<DailySession(student={self.student_id}, date={self.session_date}, "
            f"completed={self.completed_questions}/{self.target_questions}, bonus={self.bonus_questions})>"
        )
