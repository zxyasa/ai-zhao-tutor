from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth.dependencies import get_token_claims, require_student_access
from ..database import get_db
from ..engine.adaptive import select_next_item
from ..models import ParentContextEvent as DBParentContextEvent
from ..services.item_service import persist_dynamic_item_if_needed

router = APIRouter()

# Metadata keys produced by the engine that must be preserved through the
# item-persistence pipeline (which only persists "core" item columns).
_ENGINE_METADATA_KEYS = ("graduated_to_index", "graduated_to_label", "worked_example")


@router.get("/next-item")
async def get_next_item(
    student_id: str | None = None,
    skill_id: Optional[str] = None,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_token_claims),
):
    """
    Fetch next item using adaptive selection logic.
    - Weakest skill priority when skill_id is not provided.
    - Mastery-based difficulty with streak adjustment.
    - Student-specific tracks for Jon and Astrid.
    - 9.1.2: graduation indicators when the student just crossed into a new stage.
    - 9.1.4: worked_example on the first attempt of any new skill.
    """
    student = require_student_access(db=db, claims=claims, student_id=student_id)
    engine_hint = _latest_engine_hint(db, parent_id=student.parent_id, student_id=student.id)
    item = select_next_item(db, student_id=student.id, skill_id=skill_id, engine_hint=engine_hint)
    if not item:
        raise HTTPException(status_code=404, detail="No items available")

    metadata = {key: item[key] for key in _ENGINE_METADATA_KEYS if key in item}
    payload = persist_dynamic_item_if_needed(db, item)
    payload.update(metadata)
    return payload


def _latest_engine_hint(db: Session, *, parent_id: str | None, student_id: str) -> str | None:
    if not parent_id:
        return None
    scoped = (
        db.query(DBParentContextEvent)
        .filter(
            DBParentContextEvent.parent_id == parent_id,
            DBParentContextEvent.student_id == student_id,
            DBParentContextEvent.engine_hint.isnot(None),
        )
        .order_by(DBParentContextEvent.created_at.desc())
        .first()
    )
    if scoped and scoped.engine_hint:
        return scoped.engine_hint

    general = (
        db.query(DBParentContextEvent)
        .filter(
            DBParentContextEvent.parent_id == parent_id,
            DBParentContextEvent.student_id.is_(None),
            DBParentContextEvent.engine_hint.isnot(None),
        )
        .order_by(DBParentContextEvent.created_at.desc())
        .first()
    )
    return general.engine_hint if general else None
