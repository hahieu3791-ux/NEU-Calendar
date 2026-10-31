from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.study_plan import (
    StudyPlanResponse, StudyPlanCreate, StudyPlanItemResponse, AIGeneratePlanRequest
)
from app.services.planner_service import PlannerService

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.get("", response_model=List[StudyPlanResponse])
def get_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PlannerService(db)
    return service.get_all(current_user.id)


@router.get("/active", response_model=Optional[StudyPlanResponse])
def get_active_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PlannerService(db)
    return service.get_active(current_user.id)


@router.get("/{plan_id}", response_model=StudyPlanResponse)
def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PlannerService(db)
    return service.get_by_id(current_user.id, plan_id)


@router.post("", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    req: StudyPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PlannerService(db)
    return service.create(current_user.id, req)


@router.post("/ai-generate", response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
async def generate_ai_plan(
    req: AIGeneratePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PlannerService(db)
    return await service.generate_ai_plan(current_user.id, req)


@router.patch("/items/{item_id}/toggle", response_model=StudyPlanItemResponse)
def toggle_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PlannerService(db)
    return service.toggle_item(current_user.id, item_id)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PlannerService(db)
    service.delete(current_user.id, plan_id)
