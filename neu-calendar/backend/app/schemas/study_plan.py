from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class StudyPlanItemBase(BaseModel):
    task_id: Optional[int] = None
    exam_id: Optional[int] = None
    title: str = Field(..., min_length=1)
    start_at: datetime
    end_at: datetime
    is_done: bool = False
    ai_reason: Optional[str] = None


class StudyPlanItemCreate(StudyPlanItemBase):
    pass


class StudyPlanItemResponse(StudyPlanItemBase):
    id: int
    plan_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudyPlanBase(BaseModel):
    title: str = Field(..., min_length=1)
    start_date: date
    end_date: date
    source: str = "manual"  # manual, ai
    status: str = "active"


class StudyPlanCreate(StudyPlanBase):
    items: Optional[List[StudyPlanItemCreate]] = []


class StudyPlanResponse(StudyPlanBase):
    id: int
    user_id: int
    items: List[StudyPlanItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIGeneratePlanRequest(BaseModel):
    start_date: Optional[date] = None
    days_ahead: int = Field(7, ge=1, le=14)
    daily_max_hours: float = Field(5.0, ge=1.0, le=8.0)
    include_breaks: bool = True
