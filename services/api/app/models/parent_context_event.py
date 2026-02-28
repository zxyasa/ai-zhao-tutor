import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from .student import Base


class ParentContextEvent(Base):
    __tablename__ = "parent_context_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    parent_id = Column(String, ForeignKey("parents.id"), nullable=False, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=True, index=True)
    tags_json = Column(Text, nullable=False, default="[]")
    free_text = Column(Text, nullable=True)
    engine_hint = Column(String, nullable=True)
    ai_insight = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    @property
    def tags(self) -> list[str]:
        try:
            parsed = json.loads(self.tags_json or "[]")
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except Exception:
            pass
        return []

    @tags.setter
    def tags(self, values: list[str]) -> None:
        self.tags_json = json.dumps(values or [], ensure_ascii=True)
