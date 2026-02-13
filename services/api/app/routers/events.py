from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
import sys
sys.path.append("../../packages/shared")

from ..database import get_db
from ..models import Event as DBEvent, Mastery as DBMastery

router = APIRouter()


@router.post("/events")
async def create_event(
    event_data: Dict,
    db: Session = Depends(get_db)
):
    """
    Record a student answer event and update mastery scores.
    """
    # Create event
    event = DBEvent(
        id=event_data["event_id"],
        student_id=event_data["student_id"],
        item_id=event_data["item_id"],
        answer_given=event_data["answer_given"],
        is_correct=event_data["is_correct"],
        time_spent=event_data["time_spent"],
        hint_requested=event_data.get("hint_requested", False),
        timestamp=event_data.get("timestamp", datetime.now())
    )

    db.add(event)

    # Update mastery
    # First get the skill_id from the item
    from ..models import Item as DBItem
    item = db.query(DBItem).filter(DBItem.id == event_data["item_id"]).first()

    if item:
        mastery = db.query(DBMastery).filter(
            DBMastery.student_id == event_data["student_id"],
            DBMastery.skill_id == item.skill_id
        ).first()

        if mastery:
            # Update existing mastery
            mastery.total_attempts += 1
            if event_data["is_correct"]:
                mastery.correct_attempts += 1
            mastery.mastery_score = mastery.correct_attempts / mastery.total_attempts
            mastery.last_updated = datetime.now()
        else:
            # Create new mastery record
            mastery = DBMastery(
                student_id=event_data["student_id"],
                skill_id=item.skill_id,
                total_attempts=1,
                correct_attempts=1 if event_data["is_correct"] else 0,
                mastery_score=1.0 if event_data["is_correct"] else 0.0,
                last_updated=datetime.now()
            )
            db.add(mastery)

    db.commit()

    return {"status": "success", "event_id": event.id}
