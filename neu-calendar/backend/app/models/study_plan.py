from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class StudyPlan(Base, TimestampMixin):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    source = Column(String(20), default="manual", nullable=False)  # manual, ai
    status = Column(String(20), default="active", nullable=False)  # active, completed, archived

    user = relationship("User", back_populates="study_plans")
    items = relationship("StudyPlanItem", back_populates="plan", cascade="all, delete-orphan")


class StudyPlanItem(Base, TimestampMixin):
    __tablename__ = "study_plan_items"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)
    is_done = Column(Boolean, default=False, nullable=False)
    ai_reason = Column(Text, nullable=True)

    plan = relationship("StudyPlan", back_populates="items")
    task = relationship("Task")
    exam = relationship("Exam")

    __table_args__ = (
        Index("idx_plan_item_time", "plan_id", "start_at"),
    )
