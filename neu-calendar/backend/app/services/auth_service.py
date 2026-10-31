from sqlalchemy.orm import Session
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister, UserLogin, Token


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def register(self, req: UserRegister) -> User:
        existing = self.user_repo.get_by_email(req.email)
        if existing:
            raise BadRequestException("Email này đã được đăng ký trong hệ thống")

        user = User(
            email=req.email.lower().strip(),
            password_hash=get_password_hash(req.password),
            full_name=req.full_name.strip(),
            student_code=req.student_code.strip() if req.student_code else None,
            cohort=req.cohort.strip() if req.cohort else None,
            faculty=req.faculty.strip() if req.faculty else None,
            role="student"
        )
        return self.user_repo.create(user)

    def login(self, req: UserLogin) -> Token:
        user = self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.password_hash):
            raise UnauthorizedException("Email hoặc mật khẩu không chính xác")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return Token(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, refresh_token_str: str) -> Token:
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Token không hợp lệ")
            user_id = int(payload.get("sub"))
        except Exception:
            raise UnauthorizedException("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("Người dùng không tồn tại")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return Token(access_token=access_token, refresh_token=refresh_token)
