from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.alert_repository import AlertRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskProgressUpdate, TaskResponse
from app.utils.timezone import get_vietnam_now, to_vietnam_tz
from app.utils.helpers import get_urgency_badge


class TaskService:
    def __init__(self, db: Session):
        self.task_repo = TaskRepository(db)
        self.course_repo = CourseRepository(db)
        self.alert_repo = AlertRepository(db)

    def _enrich_task(self, task: Task) -> TaskResponse:
        now = get_vietnam_now()
        due_at = to_vietnam_tz(task.due_at)
        delta_seconds = (due_at - now).total_seconds()
        hours_remaining = round(delta_seconds / 3600, 1)

        severity, label = get_urgency_badge(hours_remaining)

        res = TaskResponse.model_validate(task)
        res.hours_remaining = hours_remaining
        res.urgency_label = label
        res.urgency_severity = severity
        return res

    def get_all(
        self,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        course_id: Optional[int] = None
    ) -> List[TaskResponse]:
        tasks = self.task_repo.get_all(user_id, status, priority, course_id)
        return [self._enrich_task(t) for t in tasks]

    def get_by_id(self, user_id: int, task_id: int) -> TaskResponse:
        task = self.task_repo.get_by_id(user_id, task_id)
        if not task:
            raise NotFoundException("Công việc/Deadline không tồn tại")
        return self._enrich_task(task)

    def create(self, user_id: int, req: TaskCreate) -> TaskResponse:
        if req.course_id:
            course = self.course_repo.get_by_id(req.course_id)
            if not course:
                raise BadRequestException("Môn học không tồn tại")

        task = Task(
            user_id=user_id,
            course_id=req.course_id,
            title=req.title.strip(),
            description=req.description.strip() if req.description else None,
            due_at=req.due_at,
            priority=req.priority,
            status=req.status,
            progress=req.progress,
            estimated_hours=req.estimated_hours
        )
        created = self.task_repo.create(task)
        return self._enrich_task(created)

    def update(self, user_id: int, task_id: int, req: TaskUpdate) -> TaskResponse:
        task = self.task_repo.get_by_id(user_id, task_id)
        if not task:
            raise NotFoundException("Công việc/Deadline không tồn tại")

        if req.course_id is not None:
            if req.course_id > 0:
                course = self.course_repo.get_by_id(req.course_id)
                if not course:
                    raise BadRequestException("Môn học không tồn tại")
                task.course_id = req.course_id
            else:
                task.course_id = None

        if req.title is not None:
            task.title = req.title.strip()
        if req.description is not None:
            task.description = req.description.strip()
        if req.due_at is not None:
            task.due_at = req.due_at
        if req.priority is not None:
            task.priority = req.priority
        if req.status is not None:
            task.status = req.status
            if req.status == "done":
                task.progress = 100
        if req.progress is not None:
            task.progress = req.progress
            if req.progress == 100:
                task.status = "done"
            elif req.progress > 0 and task.status == "not_started":
                task.status = "in_progress"
        if req.estimated_hours is not None:
            task.estimated_hours = req.estimated_hours

        updated = self.task_repo.update(task)
        return self._enrich_task(updated)

    def update_progress(self, user_id: int, task_id: int, req: TaskProgressUpdate) -> TaskResponse:
        task = self.task_repo.get_by_id(user_id, task_id)
        if not task:
            raise NotFoundException("Công việc/Deadline không tồn tại")

        task.progress = req.progress
        if req.status:
            task.status = req.status
        else:
            if req.progress == 100:
                task.status = "done"
            elif req.progress > 0 and task.status == "not_started":
                task.status = "in_progress"
            elif req.progress == 0:
                task.status = "not_started"

        updated = self.task_repo.update(task)
        return self._enrich_task(updated)

    def delete(self, user_id: int, task_id: int) -> None:
        task = self.task_repo.get_by_id(user_id, task_id)
        if not task:
            raise NotFoundException("Công việc/Deadline không tồn tại")
        self.alert_repo.delete_by_ref(user_id, "task", task_id)
        self.task_repo.delete(task)
