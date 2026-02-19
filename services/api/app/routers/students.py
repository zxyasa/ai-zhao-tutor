from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Student as DBStudent

router = APIRouter()

def _serialize_student(student: DBStudent) -> dict:
    return {
        "id": student.id,
        "name": student.name,
        "year_level": student.year_level,
        "avatar": student.avatar,
        "target_daily_questions": student.target_daily_questions,
        "current_streak": student.current_streak,
        "longest_streak": student.longest_streak,
        "last_practice_date": student.last_practice_date.isoformat() if student.last_practice_date else None,
        "total_sessions": student.total_sessions,
        "created_at": student.created_at.isoformat(),
    }


@router.get("/students")
async def list_students(db: Session = Depends(get_db)):
    students = db.query(DBStudent).order_by(DBStudent.name.asc()).all()
    return [_serialize_student(student) for student in students]


@router.get("/students/{student_id}")
async def get_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(DBStudent).filter(DBStudent.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return _serialize_student(student)
