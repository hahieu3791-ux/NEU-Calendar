from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ClassSessionBase(BaseModel):
    course_id: int
    day_of_week: int = Field(..., ge=2, le=8, description="2=Thứ Hai, ..., 8=Chủ Nhật")
    start_period: int = Field(..., ge=1, le=15)
    end_period: int = Field(..., ge=1, le=15)
    start_time: Optional[str] = None  # HH:MM
    end_time: Optional[str] = None    # HH:MM
    room: str = Field(..., min_length=1)
    session_type: str = Field("lecture", description="lecture, lab, self_study")
    week_from: int = Field(1, ge=1)
    week_to: int = Field(16, ge=1)


class ClassSessionCreate(ClassSessionBase):
    pass


class ClassSessionUpdate(BaseModel):
    course_id: Optional[int] = None
    day_of_week: Optional[int] = Field(None, ge=2, le=8)
    start_period: Optional[int] = Field(None, ge=1, le=15)
    end_period: Optional[int] = Field(None, ge=1, le=15)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room: Optional[str] = None
    session_type: Optional[str] = None
    week_from: Optional[int] = None
    week_to: Optional[int] = None


class CourseBrief(BaseModel):
    id: int
    code: str
    name: str
    lecturer: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClassSessionResponse(ClassSessionBase):
    id: int
    user_id: int
    course: Optional[CourseBrief] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
