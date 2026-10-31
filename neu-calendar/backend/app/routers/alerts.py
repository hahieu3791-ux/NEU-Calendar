from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.alert import AlertResponse, AlertSummaryResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlertService(db)
    return service.get_all(current_user.id)


@router.get("/summary", response_model=AlertSummaryResponse)
def get_alert_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlertService(db)
    return service.get_summary(current_user.id)


@router.patch("/{alert_id}/read", response_model=AlertResponse)
def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlertService(db)
    return service.mark_as_read(current_user.id, alert_id)


@router.post("/mark-all-read")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlertService(db)
    count = service.mark_all_as_read(current_user.id)
    return {"message": "Đã đánh dấu tất cả cảnh báo là đã đọc", "count": count}


@router.post("/refresh", response_model=AlertSummaryResponse)
def refresh_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlertService(db)
    service.scan_user_alerts(current_user.id)
    return service.get_summary(current_user.id)
