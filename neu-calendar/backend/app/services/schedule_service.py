from datetime import date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.class_session import ClassSession
from app.repositories.class_session_repository import ClassSessionRepository
from app.repositories.course_repository import CourseRepository
from app.schemas.class_session import ClassSessionCreate, ClassSessionUpdate
from app.utils.neu_periods import get_span_time
from app.utils.timezone import get_vietnam_now
from app.utils.helpers import python_weekday_to_neu_day, get_neu_day_name


class ScheduleService:
    def __init__(self, db: Session):
        self.class_repo = ClassSessionRepository(db)
        self.course_repo = CourseRepository(db)

    def get_all(self, user_id: int) -> List[ClassSession]:
        return self.class_repo.get_all(user_id)

    def get_by_id(self, user_id: int, session_id: int) -> ClassSession:
        session = self.class_repo.get_by_id(user_id, session_id)
        if not session:
            raise NotFoundException("Lịch học không tồn tại")
        return session

    def get_today_classes(self, user_id: int, target_date: Optional[date] = None) -> List[ClassSession]:
        if not target_date:
            now = get_vietnam_now()
            target_date = now.date()
        neu_day = python_weekday_to_neu_day(target_date.weekday())
        return self.class_repo.get_by_day(user_id, neu_day)

    def get_week_classes(self, user_id: int) -> Dict[str, Any]:
        """Group week schedule by day_of_week (2 to 8)."""
        all_sessions = self.class_repo.get_all(user_id)
        grouped: Dict[int, List[ClassSession]] = {d: [] for d in range(2, 9)}
        for s in all_sessions:
            if s.day_of_week in grouped:
                grouped[s.day_of_week].append(s)

        days_data = []
        for day_num in range(2, 9):
            days_data.append({
                "day_of_week": day_num,
                "day_name": get_neu_day_name(day_num),
                "sessions": grouped[day_num]
            })
        return {"days": days_data, "total_sessions": len(all_sessions)}

    def create(self, user_id: int, req: ClassSessionCreate) -> ClassSession:
        # Validate course exists
        course = self.course_repo.get_by_id(req.course_id)
        if not course:
            raise BadRequestException("Môn học được chọn không hợp lệ")

        if req.start_period > req.end_period:
            raise BadRequestException("Tiết bắt đầu không được lớn hơn tiết kết thúc")

        start_time = req.start_time
        end_time = req.end_time
        if not start_time or not end_time:
            computed_start, computed_end = get_span_time(req.start_period, req.end_period)
            start_time = start_time or computed_start
            end_time = end_time or computed_end

        session = ClassSession(
            user_id=user_id,
            course_id=req.course_id,
            day_of_week=req.day_of_week,
            start_period=req.start_period,
            end_period=req.end_period,
            start_time=start_time,
            end_time=end_time,
            room=req.room.strip(),
            session_type=req.session_type,
            week_from=req.week_from,
            week_to=req.week_to
        )
        return self.class_repo.create(session)

    def update(self, user_id: int, session_id: int, req: ClassSessionUpdate) -> ClassSession:
        session = self.get_by_id(user_id, session_id)

        if req.course_id is not None:
            course = self.course_repo.get_by_id(req.course_id)
            if not course:
                raise BadRequestException("Môn học không hợp lệ")
            session.course_id = req.course_id

        if req.start_period is not None:
            session.start_period = req.start_period
        if req.end_period is not None:
            session.end_period = req.end_period

        if session.start_period > session.end_period:
            raise BadRequestException("Tiết bắt đầu không được lớn hơn tiết kết thúc")

        if req.day_of_week is not None:
            session.day_of_week = req.day_of_week
        if req.room is not None:
            session.room = req.room.strip()
        if req.session_type is not None:
            session.session_type = req.session_type
        if req.week_from is not None:
            session.week_from = req.week_from
        if req.week_to is not None:
            session.week_to = req.week_to

        if req.start_time is not None:
            session.start_time = req.start_time
        if req.end_time is not None:
            session.end_time = req.end_time

        # If times were not updated, re-sync with periods if periods changed
        if req.start_period is not None or req.end_period is not None:
            if req.start_time is None or req.end_time is None:
                calc_start, calc_end = get_span_time(session.start_period, session.end_period)
                session.start_time = req.start_time or calc_start
                session.end_time = req.end_time or calc_end

        return self.class_repo.update(session)

    def delete(self, user_id: int, session_id: int) -> None:
        session = self.get_by_id(user_id, session_id)
        self.class_repo.delete(session)
