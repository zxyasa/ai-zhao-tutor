from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .student import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    badge_key = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    unlocked_at = Column(DateTime, nullable=False)

    student = relationship("Student")

    def __repr__(self):
        return f"<Achievement(student={self.student_id}, badge={self.badge_key})>"
