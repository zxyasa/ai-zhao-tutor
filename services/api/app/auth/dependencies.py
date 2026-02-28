from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Parent as DBParent, Student as DBStudent
from .jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_token_claims(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


def require_parent(
    claims: dict = Depends(get_token_claims),
    db: Session = Depends(get_db),
) -> DBParent:
    if claims.get("role") != "parent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parent role required")

    parent = db.query(DBParent).filter(DBParent.id == claims.get("sub")).first()
    if not parent or not parent.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Parent not found or inactive")
    return parent


def require_student(
    claims: dict = Depends(get_token_claims),
    db: Session = Depends(get_db),
) -> DBStudent:
    if claims.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student role required")

    student = db.query(DBStudent).filter(DBStudent.id == claims.get("sub")).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Student not found")
    return student


def require_student_access(
    *,
    db: Session,
    claims: dict,
    student_id: str | None,
) -> DBStudent:
    """
    Resolve student-scoped access for either parent or student role.
    - parent: can access only students under parent_id == claims.sub
    - student: can access only their own student_id == claims.sub
    """
    role = claims.get("role")
    subject = claims.get("sub")

    if role == "student":
        if student_id and subject != student_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access other students")
        target_student_id = subject
    elif role == "parent":
        if not student_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="student_id is required")
        target_student_id = student_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unsupported role")

    if role == "parent":
        student = db.query(DBStudent).filter(
            DBStudent.id == target_student_id,
            DBStudent.parent_id == subject,
        ).first()
    else:
        student = db.query(DBStudent).filter(DBStudent.id == target_student_id).first()

    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student
