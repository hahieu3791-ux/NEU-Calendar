from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    id: int
    user_id: int
    type: str  # deadline_soon, overdue, exam_soon, conflict
    severity: str  # info, warning, critical
    message: str
    ref_type: Optional[str] = None
    ref_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertSummaryResponse(BaseModel):
    total_unread: int
    critical_count: int
    warning_count: int
    info_count: int
    latest_unread: List[AlertResponse] = []
