# 🎓 NEU Calendar – Smart Academic Planner

> Ứng dụng web thông minh giúp sinh viên **Đại học Kinh tế Quốc dân (NEU)** quản lý lịch học theo tiết chuẩn NEU, đếm ngược lịch thi, theo dõi deadline công việc và lập kế hoạch học tập tối ưu với trợ lý AI Copilot.

---

## 🚀 Tính năng nổi bật

1. **Lịch học thời khóa biểu**:
   - Hiển thị theo tiết học chuẩn NEU (15 tiết, ca sáng, chiều, tối).
   - Xem linh hoạt theo **Hôm nay (Timeline)** hoặc **Dạng tuần (Thứ 2 – Chủ Nhật)**.
   - Thêm, sửa, xóa ca học trực quan; kiểm tra phòng học, giảng viên và tuần học.

2. **Lịch thi tại NEU**:
   - Quản lý ngày thi, giờ thi, thời lượng, hình thức thi (trắc nghiệm máy, tự luận, vấn đáp), phòng thi và **Số báo danh (SBD)**.
   - **Đồng hồ đếm ngược ngày thi** kèm huy hiệu cảnh báo (Khẩn cấp $\le$ 3 ngày, Cảnh báo $\le$ 7 ngày).

3. **Deadline & Công việc học tập**:
   - CRUD bài tập lớn, tiểu luận, bài tập đồ án theo từng môn học.
   - Mức độ ưu tiên (Thấp, Trung bình, Cao, Khẩn cấp).
   - Thanh tiến độ %, nút tích hoàn thành nhanh, phân loại theo trạng thái.

4. **Kế hoạch học tập thông minh (Study Planner)**:
   - **✨ Tạo kế hoạch AI**: Tự động tính toán các khung giờ trống không trùng ca học chính khóa, phân bổ thời gian giải quyết deadline gấp và ôn thi.
   - Mỗi phiên học có lý do AI ngắn gọn (`ai_reason`).
   - Tích chọn hoàn thành từng phiên học, thêm phiên tự học thủ công.

5. **Hệ thống cảnh báo tự động (Alerts)**:
   - Cảnh báo deadline sắp đến hạn ($\le$ 48h), khẩn cấp ($\le$ 24h), quá hạn.
   - Cảnh báo kỳ thi cận kề ($\le$ 7 ngày, $\le$ 3 ngày).
   - Phát hiện xung đột lịch học trùng giờ hoặc phiên tự học trùng ca học trên lớp.
   - Cơ chế chống sinh trùng cảnh báo (deduplication) và quét tự động định kỳ 15 phút.

6. **NEU Copilot – Trợ lý AI**:
   - Chatbot đồng hành hỏi đáp về lịch học hôm nay, deadline cần nộp, phòng thi, số báo danh.
   - Tự động nạp dữ liệu thật của chính người dùng vào ngữ cảnh.
   - **Hỗ trợ chế độ Mock Provider**: Hoạt động hoàn hảo ngay cả khi không có API key! Hỗ trợ mở rộng kết nối OpenAI, Gemini, Anthropic.

---

## 🛠️ Công nghệ sử dụng

- **Frontend**: HTML5, CSS3, JavaScript ES modules thuần (Vanilla JS). Icon Lucide, Font Inter.
- **Backend**: Python 3.11+, FastAPI (Pydantic v2).
- **Database & ORM**: PostgreSQL, SQLAlchemy 2.x, Alembic migrations.
- **Lập lịch nền**: APScheduler (quét cảnh báo mỗi 15 phút).
- **Bảo mật**: Hash mật khẩu bằng Bcrypt, JWT Access & Refresh Token, CORS, Pydantic input validation, chống XSS.
- **Docker**: Nginx (phục vụ frontend & reverse proxy `/api`), Backend FastAPI, PostgreSQL.

---

## 🔑 Tài khoản Demo có sẵn

Hệ thống tự động seed dữ liệu mẫu thực tế của sinh viên NEU ở lần chạy đầu tiên:

| Thông tin | Giá trị |
| :--- | :--- |
| **Email** | `demo@neu.edu.vn` |
| **Mật khẩu** | `Password123!` |
| **Họ và tên** | Nguyễn Minh Anh |
| **Mã sinh viên** | `11210001` (K64) |
| **Viện / Khoa** | Viện Công nghệ thông tin & Kinh tế số (SEIT - NEU) |

*(Bạn có thể bấm trực tiếp nút **"Đăng nhập nhanh tài khoản Demo"** ngay tại màn hình đăng nhập).*

---

## 🐳 Hướng dẫn chạy bằng Docker (Khuyến nghị)

Chỉ cần một lệnh duy nhất để khởi động toàn bộ hệ thống:

```bash
# 1. Sao chép file môi trường mẫu
cp .env.example .env

# 2. Khởi chạy hệ thống bằng Docker Compose
docker compose up --build
```

Hệ thống sẽ tự động:
1. Chờ cơ sở dữ liệu PostgreSQL khởi động sẵn sàng.
2. Chạy migration Alembic để tạo đầy đủ các bảng dữ liệu.
3. Nạp dữ liệu mẫu sinh viên NEU (môn học, ca học, bài tập lớn, lịch thi, kế hoạch AI).
4. Khởi chạy máy chủ API và Nginx.

### Các địa chỉ truy cập:
- **Giao diện Web**: [http://localhost:8080](http://localhost:8080)
- **API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 💻 Hướng dẫn chạy Local (Phát triển)

### 1. Khởi chạy Backend

```bash
cd backend

# Tạo virtualenv
python -m venv .venv
# Kích hoạt (Windows PowerShell)
.venv\Scripts\Activate.ps1
# Kích hoạt (Linux / macOS)
source .venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt

# Chạy seed dữ liệu (với SQLite hoặc PostgreSQL)
python -m app.seed.seed_data

# Khởi chạy server FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Khởi chạy Frontend

Bạn có thể mở trực tiếp thư mục `frontend/` bằng bất kỳ static web server nào:

```bash
cd frontend
python -m http.server 8080
```
Truy cập [http://localhost:8080](http://localhost:8080).

---

## 🧪 Chạy Kiểm thử (Pytest)

Dự án bao gồm bộ test kiểm thử tự động toàn diện:
- Xác thực đăng ký, đăng nhập, refresh token (`test_auth.py`).
- CRUD bài tập, tính tiến độ %, lọc dữ liệu (`test_tasks.py`).
- Cơ chế sinh cảnh báo theo hạn chót, kỳ thi, chống trùng lặp (`test_alerts.py`).
- Thuật toán AI Planner: phân bổ thời gian trống không đè ca học (`test_planner.py`).
- Trợ lý hỏi đáp AI & lịch sử chat (`test_chat.py`).
- **Data Isolation**: Kiểm tra bảo mật User A tuyệt đối không truy cập được dữ liệu của User B (`test_isolation.py`).

Chạy kiểm thử:

```bash
cd backend
pytest tests -v
```

---

## ⚙️ Cấu hình Nhà cung cấp LLM (AI Provider)

Trong file `.env`:

```env
# Chọn 1 trong các chế độ: mock | gemini | openai | anthropic
LLM_PROVIDER=mock

# Nếu dùng Gemini:
# LLM_PROVIDER=gemini
# GEMINI_API_KEY=AIzaSy...

# Nếu dùng OpenAI:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-...

# Nếu dùng Anthropic:
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-...
```

*Lưu ý: Mặc định chế độ `mock` sẽ hoạt động 100% đầy đủ, thông minh và không đòi hỏi bất kỳ API key nào.*

---

## 📁 Cấu trúc thư mục

```
neu-calendar/
├── docker-compose.yml       # Cấu hình Postgres, FastAPI và Nginx
├── .env.example             # Biến môi trường mẫu
├── README.md                # Tài liệu hướng dẫn
├── nginx/
│   ├── Dockerfile           # Nginx Alpine
│   └── default.conf         # Static frontend & reverse proxy /api
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh        # Chờ DB -> migrate -> seed -> chạy uvicorn
│   ├── requirements.txt
│   ├── alembic/             # Database migrations
│   ├── tests/               # Pytest suite
│   └── app/
│       ├── main.py          # Khởi tạo FastAPI & Scheduler
│       ├── core/            # Config, database, security, exceptions, deps
│       ├── models/          # 10 SQLAlchemy models (Users, Courses, Classes, Tasks...)
│       ├── schemas/         # Pydantic v2 schemas
│       ├── repositories/    # Truy vấn DB lọc theo user_id
│       ├── services/        # Nghiệp vụ: Alert, Planner, Schedule, Chat...
│       ├── llm/             # Abstraction layer: Mock, OpenAI, Gemini, Anthropic
│       ├── routers/         # Các endpoint REST API
│       ├── utils/           # Bảng tiết NEU, múi giờ VN, helper functions
│       └── seed/            # Dữ liệu mẫu thực tế NEU & tài khoản demo
└── frontend/
    ├── *.html               # Login, Register, Dashboard, Schedule, Exams, Tasks, Planner, Chat, Profile
    ├── css/                 # base, layout, components, dashboard, schedule...
    └── js/
        ├── config.js, api.js, auth.js, nav.js, utils.js
        ├── components/      # modal.js, toast.js, alert-bell.js
        └── pages/           # login.js, dashboard.js, schedule.js...
```
