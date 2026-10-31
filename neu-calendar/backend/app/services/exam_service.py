from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.exam import Exam
from app.repositories.exam_repository import ExamRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.alert_repository import AlertRepository
from app.schemas.exam import ExamCreate, ExamUpdate, ExamResponse
from app.utils.timezone import get_vietnam_now


class ExamService:
    def __init__(self, db: Session):
        self.exam_repo = ExamRepository(db)
        self.course_repo = CourseRepository(db)
        self.alert_repo = AlertRepository(db)

    def _enrich_exam(self, exam: Exam) -> ExamResponse:
        today = get_vietnam_now().date()
        diff = (exam.exam_date - today).days
        urgency = "normal"
        if diff < 0:
            urgency = "past"
        elif diff <= 3:
            urgency = "critical"
        elif diff <= 7:
            urgency = "warning"

        res = ExamResponse.model_validate(exam)
        res.countdown_days = diff
        res.urgency = urgency
        return res

    def get_all(self, user_id: int) -> List[ExamResponse]:
        exams = self.exam_repo.get_all(user_id)
        return [self._enrich_exam(e) for e in exams]

    def get_upcoming(self, user_id: int) -> List[ExamResponse]:
        today = get_vietnam_now().date()
        exams = self.exam_repo.get_upcoming(user_id, today)
        return [self._enrich_exam(e) for e in exams]

    def get_by_id(self, user_id: int, exam_id: int) -> ExamResponse:
        exam = self.exam_repo.get_by_id(user_id, exam_id)
        if not exam:
            raise NotFoundException("Lịch thi không tồn tại")
        return self._enrich_exam(exam)

    def create(self, user_id: int, req: ExamCreate) -> ExamResponse:
        course = self.course_repo.get_by_id(req.course_id)
        if not course:
            raise BadRequestException("Môn học không hợp lệ")

        exam = Exam(
            user_id=user_id,
            course_id=req.course_id,
            exam_date=req.exam_date,
            start_time=req.start_time,
            duration_minutes=req.duration_minutes,
            room=req.room.strip(),
            exam_type=req.exam_type,
            seat_number=req.seat_number.strip() if req.seat_number else None,
            notes=req.notes.strip() if req.notes else None
        )
        created = self.exam_repo.create(exam)
        return self._enrich_exam(created)

    def update(self, user_id: int, exam_id: int, req: ExamUpdate) -> ExamResponse:
        exam = self.exam_repo.get_by_id(user_id, exam_id)
        if not exam:
            raise NotFoundException("Lịch thi không tồn tại")

        if req.course_id is not None:
            course = self.course_repo.get_by_id(req.course_id)
            if not course:
                raise BadRequestException("Môn học không hợp lệ")
            exam.course_id = req.course_id

        if req.exam_date is not None:
            exam.exam_date = req.exam_date
        if req.start_time is not None:
            exam.start_time = req.start_time
        if req.duration_minutes is not None:
            exam.duration_minutes = req.duration_minutes
        if req.room is not None:
            exam.room = req.room.strip()
        if req.exam_type is not None:
            exam.exam_type = req.exam_type
        if req.seat_number is not None:
            exam.seat_number = req.seat_number.strip()
        if req.notes is not None:
            exam.notes = req.notes.strip()

        updated = self.exam_repo.update(exam)
        return self._enrich_exam(updated)

    def delete(self, user_id: int, exam_id: int) -> None:
        exam = self.exam_repo.get_by_id(user_id, exam_id)
        if not exam:
            raise NotFoundException("Lịch thi không tồn tại")
        self.alert_repo.delete_by_ref(user_id, "exam", exam_id)
        self.exam_repo.delete(exam)
