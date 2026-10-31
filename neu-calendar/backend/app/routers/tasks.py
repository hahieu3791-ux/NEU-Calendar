from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate, TaskProgressUpdate
from app.services.task_service import TaskService
from app.services.alert_service import AlertService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
def get_tasks(
    status: Optional[str] = Query(None, description="not_started, in_progress, done"),
    priority: Optional[str] = Query(None, description="low, medium, high, critical"),
    course_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TaskService(db)
    return service.get_all(current_user.id, status=status, priority=priority, course_id=course_id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TaskService(db)
    return service.get_by_id(current_user.id, task_id)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    req: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TaskService(db)
    created = service.create(current_user.id, req)
    AlertService(db).scan_user_alerts(current_user.id)
    return created


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    req: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TaskService(db)
    updated = service.update(current_user.id, task_id, req)
    AlertService(db).scan_user_alerts(current_user.id)
    return updated


@router.patch("/{task_id}/progress", response_model=TaskResponse)
def update_task_progress(
    task_id: int,
    req: TaskProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TaskService(db)
    updated = service.update_progress(current_user.id, task_id, req)
    AlertService(db).scan_user_alerts(current_user.id)
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TaskService(db)
    service.delete(current_user.id, task_id)
    AlertService(db).scan_user_alerts(current_user.id)
