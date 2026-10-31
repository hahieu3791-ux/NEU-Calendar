from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.class_session import ClassSession


class ClassSessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: int) -> List[ClassSession]:
        return (
            self.db.query(ClassSession)
            .options(joinedload(ClassSession.course))
            .filter(ClassSession.user_id == user_id)
            .order_by(ClassSession.day_of_week.asc(), ClassSession.start_period.asc())
            .all()
        )

    def get_by_id(self, user_id: int, session_id: int) -> Optional[ClassSession]:
        return (
            self.db.query(ClassSession)
            .options(joinedload(ClassSession.course))
            .filter(ClassSession.user_id == user_id, ClassSession.id == session_id)
            .first()
        )

    def get_by_day(self, user_id: int, day_of_week: int) -> List[ClassSession]:
        return (
            self.db.query(ClassSession)
            .options(joinedload(ClassSession.course))
            .filter(ClassSession.user_id == user_id, ClassSession.day_of_week == day_of_week)
            .order_by(ClassSession.start_period.asc())
            .all()
        )

    def create(self, session: ClassSession) -> ClassSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update(self, session: ClassSession) -> ClassSession:
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, session: ClassSession) -> None:
        self.db.delete(session)
        self.db.commit()
