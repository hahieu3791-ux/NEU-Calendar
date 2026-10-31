from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.models.alert import Alert
from app.repositories.alert_repository import AlertRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.class_session_repository import ClassSessionRepository
from app.repositories.study_plan_repository import StudyPlanRepository
from app.schemas.alert import AlertResponse, AlertSummaryResponse
from app.utils.timezone import get_vietnam_now, to_vietnam_tz, format_vietnam_datetime
from app.utils.helpers import is_time_overlapping, python_weekday_to_neu_day, get_neu_day_name


class AlertService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_repo = AlertRepository(db)
        self.task_repo = TaskRepository(db)
        self.exam_repo = ExamRepository(db)
        self.class_repo = ClassSessionRepository(db)
        self.plan_repo = StudyPlanRepository(db)

    def get_all(self, user_id: int) -> List[Alert]:
        return self.alert_repo.get_all(user_id)

    def get_summary(self, user_id: int) -> AlertSummaryResponse:
        unread = self.alert_repo.get_unread(user_id)
        critical_count = sum(1 for a in unread if a.severity == "critical")
        warning_count = sum(1 for a in unread if a.severity == "warning")
        info_count = sum(1 for a in unread if a.severity == "info")
        latest = [AlertResponse.model_validate(a) for a in unread[:5]]

        return AlertSummaryResponse(
            total_unread=len(unread),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            latest_unread=latest
        )

    def mark_as_read(self, user_id: int, alert_id: int) -> AlertResponse:
        alert = self.alert_repo.mark_as_read(user_id, alert_id)
        if not alert:
            raise NotFoundException("Cảnh báo không tồn tại")
        return AlertResponse.model_validate(alert)

    def mark_all_as_read(self, user_id: int) -> int:
        return self.alert_repo.mark_all_as_read(user_id)

    def scan_user_alerts(self, user_id: int) -> int:
        """Scan and generate all alerts for user according to business rules."""
        created_count = 0
        now = get_vietnam_now()

        # 1. Scan Tasks / Deadlines
        tasks = self.task_repo.get_all(user_id)
        for task in tasks:
            if task.status == "done":
                continue
            due_at = to_vietnam_tz(task.due_at)
            hours_diff = (due_at - now).total_seconds() / 3600.0

            alert_type = None
            severity = None
            msg = ""

            if hours_diff < 0:
                alert_type = "overdue"
                severity = "critical"
                msg = f"Deadline quá hạn: Bài tập '{task.title}' đã quá hạn nộp ({format_vietnam_datetime(due_at)})!"
            elif hours_diff <= 24:
                alert_type = "deadline_soon"
                severity = "critical"
                msg = f"Khẩn cấp (≤ 24h): Bài tập '{task.title}' hết hạn lúc {format_vietnam_datetime(due_at)} (còn {int(hours_diff)} giờ)!"
            elif hours_diff <= 48:
                alert_type = "deadline_soon"
                severity = "warning"
                msg = f"Sắp đến hạn (≤ 48h): Bài tập '{task.title}' hết hạn lúc {format_vietnam_datetime(due_at)}."

            if alert_type and severity:
                created = self._upsert_alert(
                    user_id=user_id,
                    alert_type=alert_type,
                    severity=severity,
                    message=msg,
                    ref_type="task",
                    ref_id=task.id
                )
                if created:
                    created_count += 1

        # 2. Scan Exams
        exams = self.exam_repo.get_all(user_id)
        today = now.date()
        for exam in exams:
            days_diff = (exam.exam_date - today).days
            course_name = exam.course.name if exam.course else "Môn học"

            alert_type = None
            severity = None
            msg = ""

            if 0 <= days_diff <= 3:
                alert_type = "exam_soon"
                severity = "critical"
                msg = f"Kỳ thi cận kề: Môn '{course_name}' sẽ thi vào ngày {exam.exam_date.strftime('%d/%m/%Y')} lúc {exam.start_time} (còn {days_diff} ngày) tại phòng {exam.room}!"
            elif 3 < days_diff <= 7:
                alert_type = "exam_soon"
                severity = "warning"
                msg = f"Lịch thi sắp tới: Môn '{course_name}' sẽ thi vào ngày {exam.exam_date.strftime('%d/%m/%Y')} (còn {days_diff} ngày)."

            if alert_type and severity:
                created = self._upsert_alert(
                    user_id=user_id,
                    alert_type=alert_type,
                    severity=severity,
                    message=msg,
                    ref_type="exam",
                    ref_id=exam.id
                )
                if created:
                    created_count += 1

        # 3. Scan Schedule Conflicts (Overlapping classes)
        classes = self.class_repo.get_all(user_id)
        for i in range(len(classes)):
            for j in range(i + 1, len(classes)):
                c1 = classes[i]
                c2 = classes[j]
                # Check same day of week and overlapping week ranges
                if c1.day_of_week == c2.day_of_week:
                    week_overlap = not (c1.week_to < c2.week_from or c2.week_to < c1.week_from)
                    if week_overlap and is_time_overlapping(c1.start_time, c1.end_time, c2.start_time, c2.end_time):
                        day_name = get_neu_day_name(c1.day_of_week)
                        msg = (
                            f"Xung đột lịch học vào {day_name}: Ca '{c1.course.name if c1.course else ''}' "
                            f"({c1.start_time}-{c1.end_time}) trùng giờ với '{c2.course.name if c2.course else ''}' "
                            f"({c2.start_time}-{c2.end_time})!"
                        )
                        created = self._upsert_alert(
                            user_id=user_id,
                            alert_type="conflict",
                            severity="critical",
                            message=msg,
                            ref_type="class_session",
                            ref_id=c1.id
                        )
                        if created:
                            created_count += 1

        # 4. Scan Conflict between Active Study Plan and Class Sessions
        active_plan = self.plan_repo.get_active(user_id)
        if active_plan:
            for item in active_plan.items:
                if item.is_done:
                    continue
                item_start = to_vietnam_tz(item.start_at)
                item_end = to_vietnam_tz(item.end_at)
                item_neu_day = python_weekday_to_neu_day(item_start.date().weekday())
                item_start_str = item_start.strftime("%H:%M")
                item_end_str = item_end.strftime("%H:%M")

                for c in classes:
                    if c.day_of_week == item_neu_day:
                        if is_time_overlapping(item_start_str, item_end_str, c.start_time, c.end_time):
                            msg = (
                                f"Xung đột kế hoạch tự học: Mục '{item.title}' ({item_start_str}-{item_end_str}) "
                                f"trùng ca học trên lớp '{c.course.name if c.course else ''}'!"
                            )
                            created = self._upsert_alert(
                                user_id=user_id,
                                alert_type="conflict",
                                severity="warning",
                                message=msg,
                                ref_type="plan_item",
                                ref_id=item.id
                            )
                            if created:
                                created_count += 1

        return created_count

    def _upsert_alert(
        self,
        user_id: int,
        alert_type: str,
        severity: str,
        message: str,
        ref_type: Optional[str] = None,
        ref_id: Optional[int] = None
    ) -> bool:
        existing = self.alert_repo.get_existing(user_id, alert_type, ref_type, ref_id)
        if existing:
            # If exists and unread, update message or severity if changed
            if not existing.is_read:
                if existing.severity != severity or existing.message != message:
                    existing.severity = severity
                    existing.message = message
                    self.db.commit()
            return False

        # Create new alert
        new_alert = Alert(
            user_id=user_id,
            type=alert_type,
            severity=severity,
            message=message,
            ref_type=ref_type,
            ref_id=ref_id,
            is_read=False
        )
        self.alert_repo.create(new_alert)
        return True
