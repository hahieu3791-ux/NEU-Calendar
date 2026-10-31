import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.llm.factory import get_llm_provider
from app.llm.prompts import STUDENT_COPILOT_SYSTEM_PROMPT
from app.models.chat import ChatMessage
from app.repositories.chat_repository import ChatRepository
from app.repositories.user_repository import UserRepository
from app.repositories.class_session_repository import ClassSessionRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageResponse
from app.utils.timezone import get_vietnam_now, to_vietnam_tz, format_vietnam_datetime
from app.utils.helpers import python_weekday_to_neu_day, get_neu_day_name


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.user_repo = UserRepository(db)
        self.class_repo = ClassSessionRepository(db)
        self.exam_repo = ExamRepository(db)
        self.task_repo = TaskRepository(db)

    def get_history(self, user_id: int) -> List[ChatMessage]:
        return self.chat_repo.get_history(user_id)

    def clear_history(self, user_id: int) -> None:
        self.chat_repo.clear_history(user_id)

    def _build_student_context(self, user_id: int) -> Dict[str, Any]:
        user = self.user_repo.get_by_id(user_id)
        now = get_vietnam_now()
        today_date = now.date()
        today_neu_day = python_weekday_to_neu_day(today_date.weekday())

        # Today's classes
        today_sessions = self.class_repo.get_by_day(user_id, today_neu_day)
        today_classes = [
            {
                "course_code": s.course.code if s.course else "",
                "course_name": s.course.name if s.course else "",
                "lecturer": s.course.lecturer if s.course else "",
                "start_period": s.start_period,
                "end_period": s.end_period,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "room": s.room,
                "session_type": s.session_type,
            }
            for s in today_sessions
        ]

        # Upcoming exams
        exams = self.exam_repo.get_upcoming(user_id, today_date)
        exams_list = [
            {
                "id": e.id,
                "course_code": e.course.code if e.course else "",
                "course_name": e.course.name if e.course else "",
                "exam_date": e.exam_date.strftime("%d/%m/%Y"),
                "start_time": e.start_time,
                "duration": f"{e.duration_minutes} phút",
                "room": e.room,
                "exam_type": e.exam_type,
                "seat_number": e.seat_number,
                "countdown_text": f"còn {(e.exam_date - today_date).days} ngày"
            }
            for e in exams[:5]
        ]

        # Tasks
        tasks = self.task_repo.get_all(user_id)
        tasks_list = [
            {
                "id": t.id,
                "title": t.title,
                "course_name": t.course.name if t.course else "Chung",
                "due_at": format_vietnam_datetime(to_vietnam_tz(t.due_at)),
                "priority": t.priority,
                "status": t.status,
                "progress": t.progress
            }
            for t in tasks if t.status != "done"
        ]

        return {
            "full_name": user.full_name if user else "Sinh viên",
            "student_code": user.student_code if user else "",
            "cohort": user.cohort if user else "",
            "current_time": format_vietnam_datetime(now),
            "today_day_name": get_neu_day_name(today_neu_day),
            "today_classes": today_classes,
            "exams": exams_list,
            "tasks": tasks_list
        }

    async def send_message(self, user_id: int, req: ChatRequest) -> ChatResponse:
        # Save user message
        user_msg = ChatMessage(
            user_id=user_id,
            role="user",
            content=req.message.strip()
        )
        saved_user_msg = self.chat_repo.create(user_msg)

        # Build context
        context = self._build_student_context(user_id)
        context_json_str = json.dumps(context, ensure_ascii=False, indent=2)
        system_prompt = STUDENT_COPILOT_SYSTEM_PROMPT.format(student_context_json=context_json_str)

        # Retrieve recent history
        recent_history = self.chat_repo.get_history(user_id, limit=8)
        history_formatted = [
            {"role": m.role, "content": m.content}
            for m in recent_history if m.id != saved_user_msg.id
        ]

        # Call provider
        provider = get_llm_provider()
        try:
            assistant_reply = await provider.generate_chat_response(
                system_prompt=system_prompt,
                chat_history=history_formatted,
                user_message=req.message.strip(),
                student_context=context
            )
        except Exception as e:
            assistant_reply = (
                "Xin lỗi bạn, hiện tại kết nối trợ lý AI đang gặp gián đoạn nhẹ. "
                "Tuy nhiên bạn vẫn có thể xem lịch học và deadline cập nhật trên Dashboard nhé!"
            )

        # Save assistant message
        asst_msg = ChatMessage(
            user_id=user_id,
            role="assistant",
            content=assistant_reply
        )
        saved_asst_msg = self.chat_repo.create(asst_msg)

        quick_suggestions = [
            "Hôm nay mình có ca học nào không?",
            "Các deadline bài tập cần nộp tuần này?",
            "Lịch thi và số báo danh môn tiếp theo?",
            "Gợi ý chiến lược ôn thi giữa kỳ hiệu quả"
        ]

        return ChatResponse(
            user_message=ChatMessageResponse.model_validate(saved_user_msg),
            assistant_message=ChatMessageResponse.model_validate(saved_asst_msg),
            quick_suggestions=quick_suggestions
        )
