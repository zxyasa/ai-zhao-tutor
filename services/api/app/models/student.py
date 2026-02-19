from sqlalchemy import Column, String, Integer, DateTime, Date
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    year_level = Column(Integer, nullable=False)
    avatar = Column(String, nullable=False, default="star")
    target_daily_questions = Column(Integer, nullable=False, default=10)
    current_streak = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)
    last_practice_date = Column(Date, nullable=True)
    total_sessions = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)

    # Relationships
    events = relationship("Event", back_populates="student", cascade="all, delete-orphan")
    mastery = relationship("Mastery", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name}, year={self.year_level}, streak={self.current_streak})>"
