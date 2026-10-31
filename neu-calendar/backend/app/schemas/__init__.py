from app.schemas.user import (
    UserRegister, UserLogin, UserResponse, UserUpdate, ChangePassword, Token, TokenRefreshRequest
)
from app.schemas.course import SemesterResponse, CourseBase, CourseCreate, CourseUpdate, CourseResponse
from app.schemas.class_session import (
    ClassSessionBase, ClassSessionCreate, ClassSessionUpdate, ClassSessionResponse, CourseBrief
)
from app.schemas.exam import ExamBase, ExamCreate, ExamUpdate, ExamResponse
from app.schemas.task import TaskBase, TaskCreate, TaskUpdate, TaskProgressUpdate, TaskResponse
from app.schemas.study_plan import (
    StudyPlanBase, StudyPlanCreate, StudyPlanResponse,
    StudyPlanItemBase, StudyPlanItemCreate, StudyPlanItemResponse,
    AIGeneratePlanRequest
)
from app.schemas.alert import AlertResponse, AlertSummaryResponse
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageResponse
from app.schemas.support import SupportRequestCreate, SupportRequestResponse
from app.schemas.dashboard import DashboardSummaryResponse, DashboardTodayTimelineItem

__all__ = [
    "UserRegister", "UserLogin", "UserResponse", "UserUpdate", "ChangePassword", "Token", "TokenRefreshRequest",
    "SemesterResponse", "CourseBase", "CourseCreate", "CourseUpdate", "CourseResponse",
    "ClassSessionBase", "ClassSessionCreate", "ClassSessionUpdate", "ClassSessionResponse", "CourseBrief",
    "ExamBase", "ExamCreate", "ExamUpdate", "ExamResponse",
    "TaskBase", "TaskCreate", "TaskUpdate", "TaskProgressUpdate", "TaskResponse",
    "StudyPlanBase", "StudyPlanCreate", "StudyPlanResponse",
    "StudyPlanItemBase", "StudyPlanItemCreate", "StudyPlanItemResponse",
    "AIGeneratePlanRequest",
    "AlertResponse", "AlertSummaryResponse",
    "ChatRequest", "ChatResponse", "ChatMessageResponse",
    "SupportRequestCreate", "SupportRequestResponse",
    "DashboardSummaryResponse", "DashboardTodayTimelineItem"
]
