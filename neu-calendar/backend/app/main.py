import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.models import *  # Ensure all models are registered
from app.routers import (
    auth_router,
    users_router,
    courses_router,
    classes_router,
    exams_router,
    tasks_router,
    plans_router,
    alerts_router,
    chat_router,
    support_router,
    dashboard_router,
    health_router,
)
from app.services.alert_service import AlertService
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neu_calendar")

scheduler = BackgroundScheduler()


def run_scheduled_alert_scans():
    """Background task to scan and generate alerts for all users."""
    logger.info("[SCHEDULER] Running periodic alert scan...")
    db = SessionLocal()
    try:
        users = db.query(User).all()
        alert_service = AlertService(db)
        total_created = 0
        for u in users:
            total_created += alert_service.scan_user_alerts(u.id)
        logger.info(f"[SCHEDULER] Scanned {len(users)} users, generated {total_created} new alerts.")
    except Exception as e:
        logger.error(f"[SCHEDULER] Error during periodic alert scan: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing NEU Calendar API...")
    # Create DB tables if not present
    Base.metadata.create_all(bind=engine)

    # Start periodic alert scheduler (every 15 min) if not in testing mode
    if settings.ENVIRONMENT != "testing":
        scheduler.add_job(
            run_scheduled_alert_scans,
            "interval",
            minutes=settings.ALERT_SCAN_INTERVAL_MINUTES,
            id="alert_scanner",
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"Scheduler started with {settings.ALERT_SCAN_INTERVAL_MINUTES}m interval.")

    yield

    if settings.ENVIRONMENT != "testing" and scheduler.running:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown(wait=False)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Hệ thống quản lý lịch học, lịch thi, deadline và lập kế hoạch học tập với AI Copilot cho sinh viên NEU.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
# "*" cannot be used together with allow_credentials=True in browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}")
    # Return 500 JSON
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Đã xảy ra lỗi máy chủ nội bộ. Vui lòng thử lại sau."},
    )


# Mount routers
app.include_router(health_router)
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(courses_router, prefix=settings.API_V1_STR)
app.include_router(classes_router, prefix=settings.API_V1_STR)
app.include_router(exams_router, prefix=settings.API_V1_STR)
app.include_router(tasks_router, prefix=settings.API_V1_STR)
app.include_router(plans_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(support_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
