from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth.jwt import create_access_token
from ..auth.schemas import ParentLoginRequest, ParentRegisterRequest, StudentLoginRequest, TokenResponse
from ..auth.security import hash_secret, verify_secret
from ..database import get_db
from ..models import Parent as DBParent, Student as DBStudent

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse)
async def register_parent(payload: ParentRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(DBParent).filter(DBParent.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    parent = DBParent(
        id=str(uuid4()),
        email=payload.email,
        password_hash=hash_secret(payload.password),
        display_name=payload.display_name,
        is_active=True,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(parent)
    db.commit()

    token = create_access_token(subject=parent.id, role="parent")
    return TokenResponse(access_token=token, role="parent", subject=parent.id, parent_id=parent.id)


@router.post("/auth/login", response_model=TokenResponse)
async def login_parent(payload: ParentLoginRequest, db: Session = Depends(get_db)):
    parent = db.query(DBParent).filter(DBParent.email == payload.email).first()
    if not parent or not verify_secret(payload.password, parent.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not parent.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parent account is inactive")

    token = create_access_token(subject=parent.id, role="parent")
    return TokenResponse(access_token=token, role="parent", subject=parent.id, parent_id=parent.id)


@router.post("/auth/student-login", response_model=TokenResponse)
async def login_student(payload: StudentLoginRequest, db: Session = Depends(get_db)):
    student = db.query(DBStudent).filter(DBStudent.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    if not student.pin_hash:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student PIN is not configured")
    if not verify_secret(payload.pin, student.pin_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid student PIN")

    token = create_access_token(subject=student.id, role="student", parent_id=student.parent_id)
    return TokenResponse(
        access_token=token,
        role="student",
        subject=student.id,
        parent_id=student.parent_id,
    )
