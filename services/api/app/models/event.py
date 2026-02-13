from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .student import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    item_id = Column(String, ForeignKey("items.id"), nullable=False, index=True)
    answer_given = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent = Column(Float, nullable=False)
    hint_requested = Column(Boolean, default=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Relationships
    student = relationship("Student", back_populates="events")
    item = relationship("Item", back_populates="events")

    def __repr__(self):
        return f"<Event(id={self.id}, student={self.student_id}, correct={self.is_correct})>"
