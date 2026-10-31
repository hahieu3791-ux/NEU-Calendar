from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SemesterResponse(BaseModel):
    id: int
    name: str
    start_date: str
    end_date: str
    is_current: bool

    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    code: str
    name: str
    credits: int = 3
    lecturer: Optional[str] = None
    semester_id: int


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    credits: Optional[int] = None
    lecturer: Optional[str] = None
    semester_id: Optional[int] = None


class CourseResponse(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
