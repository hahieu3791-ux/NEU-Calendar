from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.class_session import CourseBrief


class TaskBase(BaseModel):
    course_id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    due_at: datetime
    priority: str = Field("medium", pattern="^(low|medium|high|critical)$")
    status: str = Field("not_started", pattern="^(not_started|in_progress|done)$")
    progress: int = Field(0, ge=0, le=100)
    estimated_hours: float = Field(2.0, ge=0.5, le=100.0)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    course_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    status: Optional[str] = Field(None, pattern="^(not_started|in_progress|done)$")
    progress: Optional[int] = Field(None, ge=0, le=100)
    estimated_hours: Optional[float] = Field(None, ge=0.5, le=100.0)


class TaskProgressUpdate(BaseModel):
    progress: int = Field(..., ge=0, le=100)
    status: Optional[str] = Field(None, pattern="^(not_started|in_progress|done)$")


class TaskResponse(TaskBase):
    id: int
    user_id: int
    course: Optional[CourseBrief] = None
    hours_remaining: Optional[float] = None
    urgency_label: Optional[str] = None
    urgency_severity: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
