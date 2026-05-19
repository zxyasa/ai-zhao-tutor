from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.orm import Session


class TrackPlugin(ABC):
    @property
    @abstractmethod
    def student_id(self) -> str:
        ...

    @abstractmethod
    def build_item(
        self,
        db: Session,
        *,
        allowed_skills: Optional[set[str]] = None,
    ) -> Optional[dict]:
        ...
