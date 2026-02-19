from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Achievement as DBAchievement, Student as DBStudent

router = APIRouter()


@router.get("/achievements/{student_id}")
async def get_achievements(student_id: str, db: Session = Depends(get_db)):
    student = db.query(DBStudent).filter(DBStudent.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    achievements = db.query(DBAchievement).filter(
        DBAchievement.student_id == student_id
    ).order_by(DBAchievement.unlocked_at.desc()).all()

    return [
        {
            "id": achievement.id,
            "student_id": achievement.student_id,
            "badge_key": achievement.badge_key,
            "title": achievement.title,
            "description": achievement.description,
            "unlocked_at": achievement.unlocked_at.isoformat(),
        }
        for achievement in achievements
    ]
