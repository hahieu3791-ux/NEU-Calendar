from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.task import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        course_id: Optional[int] = None
    ) -> List[Task]:
        query = (
            self.db.query(Task)
            .options(joinedload(Task.course))
            .filter(Task.user_id == user_id)
        )
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if course_id:
            query = query.filter(Task.course_id == course_id)
        return query.order_by(Task.due_at.asc()).all()

    def get_upcoming_active(self, user_id: int, limit: int = 10) -> List[Task]:
        """Fetch incomplete tasks sorted by deadline ascending."""
        return (
            self.db.query(Task)
            .options(joinedload(Task.course))
            .filter(Task.user_id == user_id, Task.status != "done")
            .order_by(Task.due_at.asc())
            .limit(limit)
            .all()
        )

    def get_by_id(self, user_id: int, task_id: int) -> Optional[Task]:
        return (
            self.db.query(Task)
            .options(joinedload(Task.course))
            .filter(Task.user_id == user_id, Task.id == task_id)
            .first()
        )

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()
