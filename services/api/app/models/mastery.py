from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .student import Base


class Mastery(Base):
    __tablename__ = "mastery"

    student_id = Column(String, ForeignKey("students.id"), primary_key=True)
    skill_id = Column(String, primary_key=True, index=True)
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    mastery_score = Column(Float, default=0.0, nullable=False)
    last_updated = Column(DateTime, nullable=False)

    # Relationships
    student = relationship("Student", back_populates="mastery")

    def __repr__(self):
        return f"<Mastery(student={self.student_id}, skill={self.skill_id}, score={self.mastery_score:.2f})>"
