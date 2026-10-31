from typing import List
from sqlalchemy.orm import Session
from app.models.support import SupportRequest
from app.repositories.support_repository import SupportRepository
from app.schemas.support import SupportRequestCreate, SupportRequestResponse


class SupportService:
    def __init__(self, db: Session):
        self.support_repo = SupportRepository(db)

    def get_by_user(self, user_id: int) -> List[SupportRequest]:
        return self.support_repo.get_by_user(user_id)

    def create(self, user_id: int, req: SupportRequestCreate) -> SupportRequest:
        support_req = SupportRequest(
            user_id=user_id,
            subject=req.subject.strip(),
            message=req.message.strip(),
            status="pending"
        )
        return self.support_repo.create(support_req)
