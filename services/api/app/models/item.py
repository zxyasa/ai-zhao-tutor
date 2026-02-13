from sqlalchemy import Column, String, Integer, JSON, Text
from sqlalchemy.orm import relationship
from .student import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True)
    skill_id = Column(String, nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    difficulty = Column(Integer, nullable=False, index=True)
    parameters = Column(JSON, nullable=False)
    correct_answer = Column(String, nullable=False)
    hint = Column(Text)
    explanation = Column(Text, nullable=False)
    validation_rule = Column(String, nullable=False, default="exact_match")

    # Relationships
    events = relationship("Event", back_populates="item")

    def __repr__(self):
        return f"<Item(id={self.id}, skill={self.skill_id}, difficulty={self.difficulty})>"
