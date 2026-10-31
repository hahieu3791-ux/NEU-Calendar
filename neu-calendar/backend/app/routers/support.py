from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.support import SupportRequestCreate, SupportRequestResponse
from app.services.support_service import SupportService

router = APIRouter(prefix="/support", tags=["Support"])


@router.get("", response_model=List[SupportRequestResponse])
def get_support_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SupportService(db)
    return service.get_by_user(current_user.id)


@router.post("", response_model=SupportRequestResponse, status_code=status.HTTP_201_CREATED)
def create_support_request(
    req: SupportRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = SupportService(db)
    return service.create(current_user.id, req)
