from datetime import datetime, date, time
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.class_session_repository import ClassSessionRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.study_plan_repository import StudyPlanRepository
from app.repositories.alert_repository import AlertRepository
from app.schemas.dashboard import DashboardSummaryResponse, DashboardTodayTimelineItem
from app.schemas.exam import ExamResponse
from app.schemas.task import TaskResponse
from app.schemas.alert import AlertResponse
from app.services.exam_service import ExamService
from app.services.task_service import TaskService
from app.utils.timezone import get_vietnam_now, to_vietnam_tz, format_vietnam_datetime
from app.utils.helpers import python_weekday_to_neu_day, get_neu_day_name, time_str_to_minutes


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.course_repo = CourseRepository(db)
        self.class_repo = ClassSessionRepository(db)
        self.exam_service = ExamService(db)
        self.task_service = TaskService(db)
        self.plan_repo = StudyPlanRepository(db)
        self.alert_repo = AlertRepository(db)

    def get_summary(self, user_id: int) -> DashboardSummaryResponse:
        user = self.user_repo.get_by_id(user_id)
        first_name = user.full_name.split()[-1] if user and user.full_name else "bạn"

        now = get_vietnam_now()
        current_hour = now.hour

        if 5 <= current_hour < 12:
            greeting = f"Chào buổi sáng, {first_name}!"
        elif 12 <= current_hour < 18:
            greeting = f"Chào buổi chiều, {first_name}!"
        else:
            greeting = f"Chào buổi tối, {first_name}!"

        # Current date text
        today_date = now.date()
        today_neu_day = python_weekday_to_neu_day(today_date.weekday())
        day_name = get_neu_day_name(today_neu_day).upper()
        current_date_text = f"{day_name}, NGÀY {today_date.day:02d} THÁNG {today_date.month:02d}, {today_date.year}"

        # Current semester
        curr_sem = self.course_repo.get_current_semester()
        semester_name = curr_sem.name if curr_sem else "Học kỳ I (2024 - 2025)"

        # 1. Timeline items for today: Classes + Study plan items
        classes = self.class_repo.get_by_day(user_id, today_neu_day)
        timeline_items: List[DashboardTodayTimelineItem] = []

        for c in classes:
            c_name = c.course.name if c.course else "Môn học"
            lecturer_text = f"Giảng viên: {c.course.lecturer}" if c.course and c.course.lecturer else ""
            badge_text = "LỊCH HỌC TRÊN LỚP" if c.session_type == "lecture" else "THỰC HÀNH / LAB"
            timeline_items.append(
                DashboardTodayTimelineItem(
                    id=f"class_{c.id}",
                    item_type="class",
                    title=c_name,
                    subtitle=f"Phòng {c.room} • {lecturer_text} • Tiết {c.start_period} - {c.end_period}",
                    start_time=c.start_time,
                    end_time=c.end_time,
                    location=f"Phòng {c.room}",
                    badge_text=badge_text,
                    badge_variant="lecture"
                )
            )

        # Plan items for today
        active_plan = self.plan_repo.get_active(user_id)
        self_study_count = 0
        if active_plan:
            for item in active_plan.items:
                item_start = to_vietnam_tz(item.start_at)
                if item_start.date() == today_date:
                    self_study_count += 1
                    item_end = to_vietnam_tz(item.end_at)
                    badge_variant = "ai_suggested" if active_plan.source == "ai" else "self_study"
                    badge_label = "PHIÊN AI ĐỀ XUẤT" if active_plan.source == "ai" else "PHIÊN TỰ HỌC"
                    timeline_items.append(
                        DashboardTodayTimelineItem(
                            id=f"plan_{item.id}",
                            item_type="self_study",
                            title=item.title,
                            subtitle=item.ai_reason or "Tự học theo kế hoạch cá nhân",
                            start_time=item_start.strftime("%H:%M"),
                            end_time=item_end.strftime("%H:%M"),
                            location="Tự học cá nhân",
                            badge_text=badge_label,
                            badge_variant=badge_variant
                        )
                    )

        # Sort timeline by start_time
        timeline_items.sort(key=lambda x: time_str_to_minutes(x.start_time))

        # 2. Upcoming tasks (top 3)
        all_tasks = self.task_service.get_all(user_id)
        incomplete_tasks = [t for t in all_tasks if t.status != "done"]
        urgent_tasks_count = sum(1 for t in incomplete_tasks if t.priority in ["high", "critical"])
        top_tasks = incomplete_tasks[:3]

        # 3. Nearest exam
        upcoming_exams = self.exam_service.get_upcoming(user_id)
        nearest_exam = upcoming_exams[0] if upcoming_exams else None

        # 4. Top unread alert banner
        unread_alerts = self.alert_repo.get_unread(user_id)
        top_alert = None
        if unread_alerts:
            # Prefer critical alert first, then warning
            critical_alerts = [a for a in unread_alerts if a.severity == "critical"]
            top_alert_model = critical_alerts[0] if critical_alerts else unread_alerts[0]
            top_alert = AlertResponse.model_validate(top_alert_model)

        subtitle_summary = (
            f"Hôm nay bạn có {len(classes)} ca học trên lớp, "
            f"{self_study_count} buổi tự học và "
            f"{urgent_tasks_count} hạn chót quan trọng cần hoàn thành."
        )

        # AI Suggestion Card
        ai_suggestion = {
            "title": "Trợ lý học tập AI",
            "tag": "NEU Copilot",
            "description": (
                f"Bạn có {len(incomplete_tasks)} công việc chưa hoàn thành và "
                f"{len(upcoming_exams)} kỳ thi sắp tới. "
                "Hệ thống đề xuất bạn hoàn thành trước các deadline có mức ưu tiên cao "
                "để giải phóng thời gian ôn thi hiệu quả."
            ),
            "action_text": "Xem kế hoạch AI chi tiết",
            "action_url": "/planner.html"
        }

        # Study progress stats
        total_tasks_count = len(all_tasks)
        done_tasks_count = sum(1 for t in all_tasks if t.status == "done")
        task_completion_rate = int((done_tasks_count / total_tasks_count * 100)) if total_tasks_count > 0 else 100

        study_progress = {
            "self_study_hours": round(self_study_count * 2.0, 1),
            "completed_tasks": done_tasks_count,
            "total_tasks": total_tasks_count,
            "task_completion_rate": task_completion_rate,
            "current_week": 8,
            "total_weeks": 16
        }

        return DashboardSummaryResponse(
            greeting=greeting,
            current_date_text=current_date_text,
            semester_name=semester_name,
            subtitle_summary=subtitle_summary,
            top_alert=top_alert,
            today_timeline=timeline_items,
            upcoming_tasks=top_tasks,
            nearest_exam=nearest_exam,
            ai_suggestion=ai_suggestion,
            study_progress=study_progress
        )
