from pydantic import BaseModel, Field


class ParentRegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=256)
    display_name: str | None = Field(default=None, max_length=80)


class ParentLoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=320)
    password: str = Field(min_length=8, max_length=256)


class StudentLoginRequest(BaseModel):
    student_id: str = Field(min_length=1, max_length=120)
    pin: str = Field(min_length=4, max_length=12)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    subject: str
    parent_id: str | None = None
