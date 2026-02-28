from sqlalchemy.orm import Session

from ..models import Item as DBItem


def persist_dynamic_item_if_needed(db: Session, item_payload: dict) -> dict:
    """
    Persist custom track items outside the engine layer.
    Internal marker key is removed before payload is returned.
    """
    should_persist = bool(item_payload.get("__persist_dynamic_item"))

    if should_persist:
        item_id = item_payload["item_id"]
        exists = db.query(DBItem).filter(DBItem.id == item_id).first()
        if not exists:
            db.add(
                DBItem(
                    id=item_payload["item_id"],
                    skill_id=item_payload["skill_id"],
                    question_text=item_payload["question_text"],
                    question_type=item_payload["question_type"],
                    difficulty=item_payload["difficulty"],
                    parameters=item_payload["parameters"],
                    correct_answer=item_payload["correct_answer"],
                    hint=item_payload.get("hint"),
                    explanation=item_payload["explanation"],
                    validation_rule=item_payload.get("validation_rule", "numeric"),
                )
            )
            db.commit()

    return {k: v for k, v in item_payload.items() if not k.startswith("__")}
