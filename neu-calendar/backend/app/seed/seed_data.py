from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.semester import Semester
from app.models.course import Course
from app.models.class_session import ClassSession
from app.models.exam import Exam
from app.models.task import Task
from app.models.study_plan import StudyPlan, StudyPlanItem
from app.services.alert_service import AlertService
from app.utils.timezone import get_vietnam_now, VIETNAM_TZ


def seed_database(db: Session) -> None:
    # Check if demo user already exists
    demo_email = "demo@neu.edu.vn"
    existing_user = db.query(User).filter(User.email == demo_email).first()
    if existing_user:
        print("[SEED] Demo user already exists, running alert scan...")
        AlertService(db).scan_user_alerts(existing_user.id)
        return

    print("[SEED] Seeding NEU Calendar sample data...")

    # 1. Create Current Semester
    today = get_vietnam_now().date()
    semester = Semester(
        name="Học kỳ I (2024 - 2025)",
        start_date=today - timedelta(days=60),
        end_date=today + timedelta(days=60),
        is_current=True
    )
    db.add(semester)
    db.flush()

    # 2. Create Courses
    c_web = Course(code="IT3080", name="Lập trình Web", credits=3, lecturer="TS. Vũ Đức Long", semester_id=semester.id)
    c_ds = Course(code="IT2010", name="Cấu trúc dữ liệu & Giải thuật", credits=3, lecturer="ThS. Lê Phương Thảo", semester_id=semester.id)
    c_net = Course(code="IT3020", name="Mạng máy tính", credits=3, lecturer="PGS.TS. Nguyễn Văn Tuấn", semester_id=semester.id)
    c_sa = Course(code="IT3090", name="Phân tích và thiết kế hệ thống", credits=3, lecturer="TS. Hoàng Mai Lan", semester_id=semester.id)
    c_os = Course(code="IT2020", name="Hệ điều hành", credits=3, lecturer="TS. Trần Văn Hùng", semester_id=semester.id)

    db.add_all([c_web, c_ds, c_net, c_sa, c_os])
    db.flush()

    # 3. Create Demo User
    demo_user = User(
        email=demo_email,
        password_hash=get_password_hash("Password123!"),
        full_name="Nguyễn Minh Anh",
        student_code="11210001",
        cohort="K64",
        faculty="Viện Công nghệ thông tin & Kinh tế số (SEIT - NEU)",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80",
        role="student"
    )
    db.add(demo_user)
    db.flush()

    # 4. Create Class Sessions (Monday=2 to Saturday=7)
    s_os = ClassSession(
        user_id=demo_user.id,
        course_id=c_os.id,
        day_of_week=2,  # Thứ Hai
        start_period=1,
        end_period=3,
        start_time="07:00",
        end_time="09:30",
        room="A1-502",
        session_type="lecture",
        week_from=1,
        week_to=16
    )
    s_web = ClassSession(
        user_id=demo_user.id,
        course_id=c_web.id,
        day_of_week=4,  # Thứ Tư
        start_period=7,
        end_period=9,
        start_time="12:45",
        end_time="15:30",
        room="B2-405",
        session_type="lecture",
        week_from=1,
        week_to=16
    )
    s_ds = ClassSession(
        user_id=demo_user.id,
        course_id=c_ds.id,
        day_of_week=5,  # Thứ Năm
        start_period=1,
        end_period=3,
        start_time="07:00",
        end_time="09:30",
        room="A1-303",
        session_type="lecture",
        week_from=1,
        week_to=16
    )
    s_net = ClassSession(
        user_id=demo_user.id,
        course_id=c_net.id,
        day_of_week=6,  # Thứ Sáu
        start_period=4,
        end_period=6,
        start_time="09:40",
        end_time="12:20",
        room="C1-201",
        session_type="lecture",
        week_from=1,
        week_to=16
    )
    s_sa = ClassSession(
        user_id=demo_user.id,
        course_id=c_sa.id,
        day_of_week=7,  # Thứ Bảy
        start_period=7,
        end_period=9,
        start_time="12:45",
        end_time="15:30",
        room="B2-302",
        session_type="lecture",
        week_from=1,
        week_to=16
    )

    db.add_all([s_os, s_web, s_ds, s_net, s_sa])
    db.flush()

    # 5. Create Exams
    ex_net = Exam(
        user_id=demo_user.id,
        course_id=c_net.id,
        exam_date=today + timedelta(days=6),
        start_time="08:00",
        duration_minutes=60,
        room="B2-201",
        exam_type="Trắc nghiệm máy",
        seat_number="042",
        notes="Đề thi 40 câu trắc nghiệm + 2 bài tập tính toán IP. Mang thẻ sinh viên."
    )
    ex_ds = Exam(
        user_id=demo_user.id,
        course_id=c_ds.id,
        exam_date=today + timedelta(days=14),
        start_time="13:30",
        duration_minutes=90,
        room="A1-502",
        exam_type="Tự luận",
        seat_number="042",
        notes="Không được sử dụng tài liệu. Tập trung cây nhị phân và đồ thị."
    )
    ex_web = Exam(
        user_id=demo_user.id,
        course_id=c_web.id,
        exam_date=today + timedelta(days=21),
        start_time="14:00",
        duration_minutes=120,
        room="B2-405",
        exam_type="Vấn đáp & Báo cáo",
        seat_number="018",
        notes="Báo cáo sản phẩm thực tế theo nhóm 2 người."
    )
    db.add_all([ex_net, ex_ds, ex_web])
    db.flush()

    # 6. Create Tasks & Deadlines
    now_dt = get_vietnam_now()
    t_web = Task(
        user_id=demo_user.id,
        course_id=c_web.id,
        title="Bài tập lớn Lập trình Web",
        description="Hoàn thiện ứng dụng NEU Calendar gồm Frontend HTML/CSS/JS thuần và Backend FastAPI kết nối DB.",
        due_at=now_dt + timedelta(days=2),
        priority="high",
        status="in_progress",
        progress=60,
        estimated_hours=6.0
    )
    t_sa = Task(
        user_id=demo_user.id,
        course_id=c_sa.id,
        title="Báo cáo Phân tích thiết kế hệ thống",
        description="Vẽ biểu đồ Use Case, Activity Diagram và Class Diagram nộp qua LMS portal.",
        due_at=now_dt + timedelta(days=4),
        priority="medium",
        status="not_started",
        progress=0,
        estimated_hours=4.0
    )
    t_ds = Task(
        user_id=demo_user.id,
        course_id=c_ds.id,
        title="Giải bài tập Cây nhị phân tìm kiếm (BST)",
        description="Cài đặt thao tác chèn, xóa và duyệt cây tiền thứ tự, trung thứ tự, hậu thứ tự.",
        due_at=now_dt + timedelta(hours=22),  # Urgent (< 24h)
        priority="critical",
        status="in_progress",
        progress=40,
        estimated_hours=3.0
    )
    t_essay = Task(
        user_id=demo_user.id,
        course_id=c_os.id,
        title="Bài tập đồng bộ tiến trình (Semaphore & Mutex)",
        description="Mô phỏng bài toán Producer-Consumer và Dining Philosophers.",
        due_at=now_dt + timedelta(days=8),
        priority="low",
        status="not_started",
        progress=0,
        estimated_hours=2.5
    )
    db.add_all([t_web, t_sa, t_ds, t_essay])
    db.flush()

    # 7. Create AI Study Plan
    plan = StudyPlan(
        user_id=demo_user.id,
        title=f"Kế hoạch học tập AI tuần {(today.isocalendar()[1] % 16) + 1}",
        start_date=today,
        end_date=today + timedelta(days=7),
        source="ai",
        status="active"
    )
    db.add(plan)
    db.flush()

    # Study plan items
    pi1 = StudyPlanItem(
        plan_id=plan.id,
        task_id=t_ds.id,
        title="Tự học Cấu trúc dữ liệu",
        start_at=datetime.combine(today, datetime.strptime("09:45", "%H:%M").time(), tzinfo=VIETNAM_TZ),
        end_at=datetime.combine(today, datetime.strptime("11:15", "%H:%M").time(), tzinfo=VIETNAM_TZ),
        is_done=False,
        ai_reason="Giải quyết dứt điểm bài tập cây nhị phân trước hạn chót cận kề."
    )
    pi2 = StudyPlanItem(
        plan_id=plan.id,
        task_id=t_web.id,
        title="Làm bài tập Lập trình Web",
        start_at=datetime.combine(today, datetime.strptime("13:30", "%H:%M").time(), tzinfo=VIETNAM_TZ),
        end_at=datetime.combine(today, datetime.strptime("15:00", "%H:%M").time(), tzinfo=VIETNAM_TZ),
        is_done=False,
        ai_reason="Tiết kiệm 2 giờ áp lực cận hạn nộp, code hoàn thiện giao diện Dashboard."
    )
    pi3 = StudyPlanItem(
        plan_id=plan.id,
        exam_id=ex_net.id,
        title="Ôn tập Mạng máy tính",
        start_at=datetime.combine(today, datetime.strptime("19:00", "%H:%M").time(), tzinfo=VIETNAM_TZ),
        end_at=datetime.combine(today, datetime.strptime("20:30", "%H:%M").time(), tzinfo=VIETNAM_TZ),
        is_done=False,
        ai_reason="Trọng tâm: Mô hình OSI & TCP/IP. Chuẩn bị trước kỳ thi giữa kỳ."
    )
    db.add_all([pi1, pi2, pi3])
    db.commit()

    # 8. Run Alert Scan for Demo User
    alert_service = AlertService(db)
    alert_service.scan_user_alerts(demo_user.id)
    print(f"[SEED] Successfully seeded NEU Calendar for user {demo_email}!")


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
