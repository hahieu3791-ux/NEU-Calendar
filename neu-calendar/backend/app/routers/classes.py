from typing import List, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.class_session import ClassSessionResponse, ClassSessionCreate, ClassSessionUpdate
from app.services.schedule_service import ScheduleService
from app.services.alert_service import AlertService

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("", response_model=List[ClassSessionResponse])
def get_classes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ScheduleService(db)
    return service.get_all(current_user.id)


@router.get("/today", response_model=List[ClassSessionResponse])
def get_today_classes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ScheduleService(db)
    return service.get_today_classes(current_user.id)


@router.get("/week")
def get_week_classes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ScheduleService(db)
    return service.get_week_classes(current_user.id)


@router.get("/{session_id}", response_model=ClassSessionResponse)
def get_class(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ScheduleService(db)
    return service.get_by_id(current_user.id, session_id)


@router.post("", response_model=ClassSessionResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    req: ClassSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ScheduleService(db)
    created = service.create(current_user.id, req)
    # Refresh alert conflicts in background
    AlertService(db).scan_user_alerts(current_user.id)
    return created


@router.put("/{session_id}", response_model=ClassSessionResponse)
def update_class(
    session_id: int,
    req: ClassSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ScheduleService(db)
    updated = service.update(current_user.id, session_id, req)
    AlertService(db).scan_user_alerts(current_user.id)
    return updated


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ScheduleService(db)
    service.delete(current_user.id, session_id)
    AlertService(db).scan_user_alerts(current_user.id)
