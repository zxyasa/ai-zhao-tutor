from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class TrackPlugin(ABC):
    @property
    @abstractmethod
    def student_id(self) -> str:
        ...

    @abstractmethod
    def build_item(self, db: Session) -> dict:
        ...
