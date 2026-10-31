from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.exam import ExamResponse, ExamCreate, ExamUpdate
from app.services.exam_service import ExamService
from app.services.alert_service import AlertService

router = APIRouter(prefix="/exams", tags=["Exams"])


@router.get("", response_model=List[ExamResponse])
def get_exams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.get_all(current_user.id)


@router.get("/upcoming", response_model=List[ExamResponse])
def get_upcoming_exams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.get_upcoming(current_user.id)


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    return service.get_by_id(current_user.id, exam_id)


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(
    req: ExamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    created = service.create(current_user.id, req)
    AlertService(db).scan_user_alerts(current_user.id)
    return created


@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    req: ExamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    updated = service.update(current_user.id, exam_id, req)
    AlertService(db).scan_user_alerts(current_user.id)
    return updated


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ExamService(db)
    service.delete(current_user.id, exam_id)
    AlertService(db).scan_user_alerts(current_user.id)
