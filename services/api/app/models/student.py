from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    year_level = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # Relationships
    events = relationship("Event", back_populates="student", cascade="all, delete-orphan")
    mastery = relationship("Mastery", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name}, year={self.year_level})>"
