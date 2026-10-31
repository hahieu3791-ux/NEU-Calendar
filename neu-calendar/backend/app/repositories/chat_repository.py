from typing import List
from sqlalchemy.orm import Session
from app.models.chat import ChatMessage


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_history(self, user_id: int, limit: int = 50) -> List[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .all()
        )

    def create(self, message: ChatMessage) -> ChatMessage:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def clear_history(self, user_id: int) -> int:
        count = self.db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
        self.db.commit()
        return count
