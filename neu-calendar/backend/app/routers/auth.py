from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, Token, TokenRefreshRequest, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegister, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register(req)


@router.post("/login", response_model=Token)
def login(req: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(req)


@router.post("/refresh", response_model=Token)
def refresh(req: TokenRefreshRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh(req.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
