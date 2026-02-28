from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from .student import Base


class Parent(Base):
    __tablename__ = "parents"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False)

    students = relationship("Student", back_populates="parent")

    def __repr__(self):
        return f"<Parent(id={self.id}, email={self.email}, active={self.is_active})>"
