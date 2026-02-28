from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth.dependencies import get_token_claims, require_student_access
from ..database import get_db
from ..schemas import EventCreate
from ..services.event_processor import process_event

router = APIRouter()


@router.post("/events")
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    """
    Record a student answer event and update mastery scores.
    """
    student = require_student_access(db=db, claims=claims, student_id=event_data.student_id)
    payload = event_data.model_copy(update={"student_id": student.id})
    return process_event(db, payload)
