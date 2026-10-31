from sqlalchemy.orm import Session
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate, ChangePassword


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def get_profile(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("Người dùng không tồn tại")
        return user

    def update_profile(self, user_id: int, req: UserUpdate) -> User:
        user = self.get_profile(user_id)
        if req.full_name is not None:
            user.full_name = req.full_name.strip()
        if req.student_code is not None:
            user.student_code = req.student_code.strip()
        if req.cohort is not None:
            user.cohort = req.cohort.strip()
        if req.faculty is not None:
            user.faculty = req.faculty.strip()
        if req.avatar_url is not None:
            user.avatar_url = req.avatar_url.strip()
        return self.user_repo.update(user)

    def change_password(self, user_id: int, req: ChangePassword) -> None:
        user = self.get_profile(user_id)
        if not verify_password(req.old_password, user.password_hash):
            raise BadRequestException("Mật khẩu hiện tại không chính xác")
        user.password_hash = get_password_hash(req.new_password)
        self.user_repo.update(user)
