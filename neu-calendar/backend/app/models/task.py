from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=False, index=True)
    priority = Column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    status = Column(String(20), default="not_started", nullable=False)  # not_started, in_progress, done
    progress = Column(Integer, default=0, nullable=False)  # 0 to 100
    estimated_hours = Column(Float, default=2.0, nullable=False)

    user = relationship("User", back_populates="tasks")
    course = relationship("Course", back_populates="tasks")

    __table_args__ = (
        Index("idx_task_user_due", "user_id", "due_at"),
        Index("idx_task_user_status", "user_id", "status"),
    )
