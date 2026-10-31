import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    async def generate_chat_response(
        self,
        system_prompt: str,
        chat_history: List[Dict[str, str]],
        user_message: str,
        student_context: Dict[str, Any]
    ) -> str:
        msg = user_message.lower().strip()
        classes = student_context.get("today_classes", [])
        week_classes = student_context.get("week_classes", [])
        tasks = student_context.get("tasks", [])
        exams = student_context.get("exams", [])
        user_name = student_context.get("full_name", "bạn")

        # Check for schedule inquiry
        if any(w in msg for w in ["lịch học", "thời khóa biểu", "hôm nay học gì", "tiết mấy", "phòng nào"]):
            if classes:
                lines = [f"Chào {user_name}! Hôm nay bạn có **{len(classes)} ca học** trên lớp:"]
                for c in classes:
                    lines.append(f"- **{c.get('course_name')}** ({c.get('course_code')}): Tiết {c.get('start_period')}-{c.get('end_period')} ({c.get('start_time')} - {c.get('end_time')}) tại phòng **{c.get('room')}**, GV: {c.get('lecturer') or 'Chưa cập nhật'}.")
                lines.append("\n💡 *Lời khuyên:* Hãy đến sớm 5-10 phút để ổn định chỗ ngồi nhé!")
                return "\n".join(lines)
            else:
                return f"Chào {user_name}! Hôm nay bạn **không có ca học nào trên lớp**. Đây là cơ hội tuyệt vời để tập trung giải quyết các deadline hoặc phiên tự học đã lên kế hoạch!"

        # Check for exams inquiry
        if any(w in msg for w in ["lịch thi", "khi nào thi", "thi môn gì", "phòng thi", "số báo danh", "sbd"]):
            if exams:
                lines = [f"Dưới đây là các **kỳ thi sắp tới tại NEU** của {user_name}:"]
                for ex in exams:
                    lines.append(f"- **{ex.get('course_name')}** ({ex.get('course_code')}): Ngày **{ex.get('exam_date')}** lúc {ex.get('start_time')} | Phòng **{ex.get('room')}** | Hình thức: *{ex.get('exam_type')}* | SBD: `{ex.get('seat_number') or 'Chưa xếp'}` ({ex.get('countdown_text')}).")
                lines.append("\n⚠️ *Lưu ý:* Nhớ mang theo Thẻ sinh viên NEU và CMND/CCCD khi vào phòng thi!")
                return "\n".join(lines)
            else:
                return f"Hiện tại bạn chưa có lịch thi nào được ghi nhận trong hệ thống. Chúc bạn có thời gian học tập thoải mái!"

        # Check for deadlines/tasks inquiry
        if any(w in msg for w in ["deadline", "hạn nộp", "bài tập", "công việc", "sắp nộp"]):
            if tasks:
                urgent_tasks = [t for t in tasks if t.get("status") != "done"][:5]
                lines = [f"Chào {user_name}, bạn đang có **{len(urgent_tasks)} deadline cần hoàn thành**:"]
                for t in urgent_tasks:
                    lines.append(f"- **{t.get('title')}** (Môn: {t.get('course_name') or 'Chung'}): Hạn chót: **{t.get('due_at')}** | Ưu tiên: `{t.get('priority')}` | Tiến độ: {t.get('progress')}%")
                lines.append("\n🎯 *Gợi ý:* Hãy ưu tiên xử lý bài tập có mức ưu tiên Cao hoặc Khẩn cấp trước nhé!")
                return "\n".join(lines)
            else:
                return f"Tuyệt vời! Hiện bạn không còn deadline nào tồn đọng. Hãy dành thời gian nghỉ ngơi hoặc lập kế hoạch ôn tập dài hạn."

        # Check for study plan / advice inquiry
        if any(w in msg for w in ["kế hoạch", "ôn tập", "học tập", "tư vấn", "chiến lược", "gợi ý"]):
            urgent_tasks = [t for t in tasks if t.get("status") != "done"]
            first_task = urgent_tasks[0].get("title") if urgent_tasks else "bài tập tuần"
            first_exam = exams[0].get("course_name") if exams else "môn thi sắp tới"
            return (
                f"Dựa trên lịch học và khối lượng công việc hiện tại của {user_name}, tôi gợi ý:\n\n"
                f"1. **Tập trung cao độ cho `{first_task}`**: Dành khoảng 1.5 - 2 giờ vào khung giờ trống buổi chiều hoặc tối nay.\n"
                f"2. **Ôn tập sớm môn `{first_exam}`**: Đọc lại slide bài giảng và luyện đề trắc nghiệm NEU theo từng chương.\n"
                f"3. **Nguyên tắc Pomodoro**: Học 25 phút, nghỉ 5 phút để giữ sự tập trung cao nhất.\n\n"
                f"Bạn có thể bấm nút **'Tạo kế hoạch AI'** tại trang Kế hoạch học tập để hệ thống tự động xếp lịch tự học tối ưu!"
            )

        # Check for general out-of-scope inquiry
        if any(w in msg for w in ["bóng đá", "thời tiết", "chơi game", "chính trị", "bitcoin", "tài chính thế giới"]):
            return (
                f"Xin lỗi {user_name}, tôi là NEU Copilot – trợ lý được thiết kế chuyên biệt cho việc học tập, "
                f"thời khóa biểu và quản lý thi cử tại NEU. Tôi không hỗ trợ các chủ đề ngoài học vụ. "
                f"Hãy hỏi tôi về lịch học, lịch thi hoặc deadline của bạn nhé!"
            )

        # General friendly greeting / response
        return (
            f"Chào {user_name}! Tôi là NEU Copilot – Trợ lý học tập thông minh.\n\n"
            f"Tôi có thể hỗ trợ bạn:\n"
            f"- 📅 Tra cứu thời khóa biểu và phòng học hôm nay\n"
            f"- ⏳ Đếm ngược lịch thi và tra số báo danh\n"
            f"- ⏰ Kiểm tra danh sách deadline và cảnh báo quá hạn\n"
            f"- 🤖 Gợi ý khung giờ tự học tối ưu nhất cho tuần này\n\n"
            f"Bạn muốn xem thông tin nào ngay bây giờ?"
        )

    async def generate_study_plan_items(
        self,
        free_slots: List[Dict[str, Any]],
        tasks: List[Dict[str, Any]],
        exams: List[Dict[str, Any]],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Distribute tasks and exam prep across available free slots smartly."""
        plan_items = []
        if not free_slots:
            return plan_items

        slot_idx = 0
        total_slots = len(free_slots)

        # Prioritize tasks
        for task in tasks:
            if slot_idx >= total_slots:
                break
            slot = free_slots[slot_idx]
            slot_idx += 1
            plan_items.append({
                "task_id": task.get("id"),
                "exam_id": None,
                "title": f"Tự học: {task.get('title')}",
                "start_at": slot["start_at"],
                "end_at": slot["end_at"],
                "is_done": False,
                "ai_reason": f"Tập trung hoàn thành trước hạn {task.get('due_text', 'sắp tới')}, giảm áp lực dồn bài."
            })

        # Next prioritize upcoming exams
        for exam in exams:
            if slot_idx >= total_slots:
                break
            slot = free_slots[slot_idx]
            slot_idx += 1
            plan_items.append({
                "task_id": None,
                "exam_id": exam.get("id"),
                "title": f"Ôn thi: {exam.get('course_name') or 'Môn học'}",
                "start_at": slot["start_at"],
                "end_at": slot["end_at"],
                "is_done": False,
                "ai_reason": f"Ôn tập kiến thức trọng tâm trước ngày thi {exam.get('exam_date')}, tự tin đạt điểm cao."
            })

        # Fill remaining slots with general study / revision
        while slot_idx < min(total_slots, 6):
            slot = free_slots[slot_idx]
            slot_idx += 1
            plan_items.append({
                "task_id": None,
                "exam_id": None,
                "title": "Củng cố kiến thức & Đọc giáo trình NEU",
                "start_at": slot["start_at"],
                "end_at": slot["end_at"],
                "is_done": False,
                "ai_reason": "Khung giờ trống lý tưởng để ôn bài cũ và chuẩn bị cho buổi học tiếp theo."
            })

        return plan_items
