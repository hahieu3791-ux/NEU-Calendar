from typing import List
from sqlalchemy.orm import Session
from app.models.support import SupportRequest


class SupportRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: int) -> List[SupportRequest]:
        return (
            self.db.query(SupportRequest)
            .filter(SupportRequest.user_id == user_id)
            .order_by(SupportRequest.created_at.desc())
            .all()
        )

    def create(self, request: SupportRequest) -> SupportRequest:
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
