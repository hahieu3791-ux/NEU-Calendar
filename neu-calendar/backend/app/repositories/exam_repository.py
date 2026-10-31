from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.exam import Exam


class ExamRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: int) -> List[Exam]:
        return (
            self.db.query(Exam)
            .options(joinedload(Exam.course))
            .filter(Exam.user_id == user_id)
            .order_by(Exam.exam_date.asc(), Exam.start_time.asc())
            .all()
        )

    def get_upcoming(self, user_id: int, from_date: date) -> List[Exam]:
        return (
            self.db.query(Exam)
            .options(joinedload(Exam.course))
            .filter(Exam.user_id == user_id, Exam.exam_date >= from_date)
            .order_by(Exam.exam_date.asc(), Exam.start_time.asc())
            .all()
        )

    def get_by_id(self, user_id: int, exam_id: int) -> Optional[Exam]:
        return (
            self.db.query(Exam)
            .options(joinedload(Exam.course))
            .filter(Exam.user_id == user_id, Exam.id == exam_id)
            .first()
        )

    def create(self, exam: Exam) -> Exam:
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def update(self, exam: Exam) -> Exam:
        self.db.commit()
        self.db.refresh(exam)
        return exam

    def delete(self, exam: Exam) -> None:
        self.db.delete(exam)
        self.db.commit()
