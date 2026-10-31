from typing import List, Optional
from pydantic import BaseModel
from app.schemas.class_session import ClassSessionResponse
from app.schemas.exam import ExamResponse
from app.schemas.task import TaskResponse
from app.schemas.alert import AlertResponse


class DashboardTodayTimelineItem(BaseModel):
    id: str  # e.g., "class_1" or "plan_2"
    item_type: str  # class, self_study, task_slot, ai_suggested
    title: str
    subtitle: Optional[str] = None
    start_time: str
    end_time: str
    location: Optional[str] = None
    badge_text: str
    badge_variant: str  # lecture, self_study, deadline, ai_suggested


class DashboardSummaryResponse(BaseModel):
    greeting: str
    current_date_text: str
    semester_name: str
    subtitle_summary: str
    top_alert: Optional[AlertResponse] = None
    today_timeline: List[DashboardTodayTimelineItem] = []
    upcoming_tasks: List[TaskResponse] = []
    nearest_exam: Optional[ExamResponse] = None
    ai_suggestion: Optional[dict] = None
    study_progress: dict
