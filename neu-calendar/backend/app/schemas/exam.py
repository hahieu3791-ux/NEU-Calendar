from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.class_session import CourseBrief


class ExamBase(BaseModel):
    course_id: int
    exam_date: date
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM")
    duration_minutes: int = Field(60, ge=15, le=300)
    room: str
    exam_type: str = "Cuối kỳ"
    seat_number: Optional[str] = None
    notes: Optional[str] = None


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    course_id: Optional[int] = None
    exam_date: Optional[date] = None
    start_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    duration_minutes: Optional[int] = Field(None, ge=15, le=300)
    room: Optional[str] = None
    exam_type: Optional[str] = None
    seat_number: Optional[str] = None
    notes: Optional[str] = None


class ExamResponse(ExamBase):
    id: int
    user_id: int
    course: Optional[CourseBrief] = None
    countdown_days: Optional[int] = None
    urgency: Optional[str] = None  # critical, warning, normal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
