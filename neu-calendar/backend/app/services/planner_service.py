from datetime import datetime, date, time, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException, BadRequestException
from app.llm.factory import get_llm_provider
from app.models.study_plan import StudyPlan, StudyPlanItem
from app.repositories.study_plan_repository import StudyPlanRepository
from app.repositories.class_session_repository import ClassSessionRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.exam_repository import ExamRepository
from app.schemas.study_plan import (
    StudyPlanCreate, StudyPlanResponse, StudyPlanItemResponse, AIGeneratePlanRequest
)
from app.utils.timezone import get_vietnam_now, VIETNAM_TZ, to_vietnam_tz
from app.utils.helpers import python_weekday_to_neu_day, time_str_to_minutes


class PlannerService:
    def __init__(self, db: Session):
        self.db = db
        self.plan_repo = StudyPlanRepository(db)
        self.class_repo = ClassSessionRepository(db)
        self.task_repo = TaskRepository(db)
        self.exam_repo = ExamRepository(db)

    def get_all(self, user_id: int) -> List[StudyPlan]:
        return self.plan_repo.get_all(user_id)

    def get_active(self, user_id: int) -> Optional[StudyPlan]:
        return self.plan_repo.get_active(user_id)

    def get_by_id(self, user_id: int, plan_id: int) -> StudyPlan:
        plan = self.plan_repo.get_by_id(user_id, plan_id)
        if not plan:
            raise NotFoundException("Kế hoạch học tập không tồn tại")
        return plan

    def toggle_item(self, user_id: int, item_id: int) -> StudyPlanItem:
        item = self.plan_repo.get_item_by_id(user_id, item_id)
        if not item:
            raise NotFoundException("Mục kế hoạch không tồn tại")
        item.is_done = not item.is_done
        return self.plan_repo.update_item(item)

    def delete(self, user_id: int, plan_id: int) -> None:
        plan = self.get_by_id(user_id, plan_id)
        self.plan_repo.delete(plan)

    def create(self, user_id: int, req: StudyPlanCreate) -> StudyPlan:
        plan = StudyPlan(
            user_id=user_id,
            title=req.title,
            start_date=req.start_date,
            end_date=req.end_date,
            source=req.source,
            status=req.status
        )
        created_plan = self.plan_repo.create(plan)
        for item_in in req.items or []:
            item = StudyPlanItem(
                plan_id=created_plan.id,
                task_id=item_in.task_id,
                exam_id=item_in.exam_id,
                title=item_in.title,
                start_at=item_in.start_at,
                end_at=item_in.end_at,
                is_done=item_in.is_done,
                ai_reason=item_in.ai_reason
            )
            self.db.add(item)
        self.db.commit()
        self.db.refresh(created_plan)
        return created_plan

    def calculate_free_slots_for_period(
        self,
        user_id: int,
        start_date: date,
        days_count: int,
        daily_max_hours: float = 5.0
    ) -> List[Dict[str, Any]]:
        """Find non-overlapping study slots that never clash with classes."""
        classes = self.class_repo.get_all(user_id)
        free_slots = []

        # Available study windows per day (in minutes from midnight)
        study_windows = [
            (9 * 60 + 45, 11 * 60 + 45),  # 09:45 - 11:45 (morning)
            (14 * 60, 16 * 60 + 30),      # 14:00 - 16:30 (afternoon)
            (19 * 60, 21 * 60 + 30),      # 19:00 - 21:30 (evening)
        ]

        for day_offset in range(days_count):
            cur_date = start_date + timedelta(days=day_offset)
            neu_day = python_weekday_to_neu_day(cur_date.weekday())
            day_classes = [c for c in classes if c.day_of_week == neu_day]

            # Convert class times to minute intervals
            busy_intervals = []
            for c in day_classes:
                s_min = time_str_to_minutes(c.start_time)
                e_min = time_str_to_minutes(c.end_time)
                busy_intervals.append((s_min, e_min))

            day_study_hours = 0.0

            for win_start, win_end in study_windows:
                if day_study_hours >= daily_max_hours:
                    break

                # Check if this window conflicts with any class
                clash = False
                for b_start, b_end in busy_intervals:
                    if max(win_start, b_start) < min(win_end, b_end):
                        clash = True
                        break

                if not clash:
                    start_dt = datetime.combine(cur_date, time(win_start // 60, win_start % 60), tzinfo=VIETNAM_TZ)
                    end_dt = datetime.combine(cur_date, time(win_end // 60, win_end % 60), tzinfo=VIETNAM_TZ)
                    slot_hours = (win_end - win_start) / 60.0

                    if day_study_hours + slot_hours <= daily_max_hours:
                        free_slots.append({
                            "date": cur_date.isoformat(),
                            "start_at": start_dt,
                            "end_at": end_dt,
                            "duration_hours": slot_hours,
                        })
                        day_study_hours += slot_hours

        return free_slots

    async def generate_ai_plan(self, user_id: int, req: AIGeneratePlanRequest) -> StudyPlan:
        now = get_vietnam_now()
        start_date = req.start_date or now.date()
        end_date = start_date + timedelta(days=req.days_ahead)

        # 1. Calculate free slots
        free_slots = self.calculate_free_slots_for_period(
            user_id=user_id,
            start_date=start_date,
            days_count=req.days_ahead,
            daily_max_hours=req.daily_max_hours
        )

        if not free_slots:
            raise BadRequestException("Không tìm thấy khung giờ trống phù hợp trong khoảng thời gian đã chọn.")

        # 2. Collect pending tasks and upcoming exams
        tasks = self.task_repo.get_all(user_id)
        pending_tasks = [t for t in tasks if t.status != "done"]
        # Sort by priority and due_at
        priority_map = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        pending_tasks.sort(key=lambda t: (priority_map.get(t.priority, 2), t.due_at))

        upcoming_exams = self.exam_repo.get_upcoming(user_id, start_date)

        # 3. Format inputs for LLM provider
        tasks_data = [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "due_text": t.due_at.strftime("%d/%m %H:%M"),
                "estimated_hours": t.estimated_hours,
            }
            for t in pending_tasks[:6]
        ]

        exams_data = [
            {
                "id": e.id,
                "course_name": e.course.name if e.course else "Môn học",
                "exam_date": e.exam_date.strftime("%d/%m/%Y"),
                "start_time": e.start_time,
            }
            for e in upcoming_exams[:4]
        ]

        # 4. Invoke LLM provider (Mock or configured)
        provider = get_llm_provider()
        plan_items_data = await provider.generate_study_plan_items(
            free_slots=free_slots,
            tasks=tasks_data,
            exams=exams_data,
            options={"daily_max_hours": req.daily_max_hours, "include_breaks": req.include_breaks}
        )

        # 5. Archive existing active plan if any
        existing_active = self.plan_repo.get_active(user_id)
        if existing_active:
            existing_active.status = "archived"
            self.plan_repo.update(existing_active)

        # 6. Save new StudyPlan
        plan = StudyPlan(
            user_id=user_id,
            title=f"Kế hoạch học tập AI ({start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m/%Y')})",
            start_date=start_date,
            end_date=end_date,
            source="ai",
            status="active"
        )
        saved_plan = self.plan_repo.create(plan)

        for item_data in plan_items_data:
            start_at = item_data["start_at"]
            end_at = item_data["end_at"]
            if isinstance(start_at, str):
                start_at = datetime.fromisoformat(start_at)
            if isinstance(end_at, str):
                end_at = datetime.fromisoformat(end_at)

            item = StudyPlanItem(
                plan_id=saved_plan.id,
                task_id=item_data.get("task_id"),
                exam_id=item_data.get("exam_id"),
                title=item_data.get("title", "Phiên tự học"),
                start_at=start_at,
                end_at=end_at,
                is_done=False,
                ai_reason=item_data.get("ai_reason", "Tối ưu hóa thời gian trống.")
            )
            self.db.add(item)

        self.db.commit()
        self.db.refresh(saved_plan)
        return saved_plan
