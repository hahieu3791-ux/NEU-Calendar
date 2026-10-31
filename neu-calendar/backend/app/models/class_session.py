from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class ClassSession(Base, TimestampMixin):
    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False, index=True)  # 2: Thứ 2 ... 8: Chủ Nhật
    start_period = Column(Integer, nullable=False)
    end_period = Column(Integer, nullable=False)
    start_time = Column(String(10), nullable=False)  # HH:MM e.g. "07:00"
    end_time = Column(String(10), nullable=False)  # HH:MM e.g. "09:30"
    room = Column(String(100), nullable=False)  # e.g. "A1-502"
    session_type = Column(String(50), default="lecture", nullable=False)  # lecture, lab, self_study
    week_from = Column(Integer, default=1, nullable=False)
    week_to = Column(Integer, default=16, nullable=False)

    user = relationship("User", back_populates="class_sessions")
    course = relationship("Course", back_populates="class_sessions")

    __table_args__ = (
        Index("idx_class_user_day", "user_id", "day_of_week"),
    )
