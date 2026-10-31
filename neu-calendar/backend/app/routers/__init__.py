from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.courses import router as courses_router
from app.routers.classes import router as classes_router
from app.routers.exams import router as exams_router
from app.routers.tasks import router as tasks_router
from app.routers.plans import router as plans_router
from app.routers.alerts import router as alerts_router
from app.routers.chat import router as chat_router
from app.routers.support import router as support_router
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router

__all__ = [
    "auth_router",
    "users_router",
    "courses_router",
    "classes_router",
    "exams_router",
    "tasks_router",
    "plans_router",
    "alerts_router",
    "chat_router",
    "support_router",
    "dashboard_router",
    "health_router",
]
