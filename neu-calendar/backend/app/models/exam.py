from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Exam(Base, TimestampMixin):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_date = Column(Date, nullable=False, index=True)
    start_time = Column(String(10), nullable=False)  # HH:MM e.g. "08:00"
    duration_minutes = Column(Integer, default=60, nullable=False)  # e.g. 60, 90
    room = Column(String(100), nullable=False)  # e.g. "B2-201"
    exam_type = Column(String(50), default="Cuối kỳ", nullable=False)  # Giữa kỳ, Cuối kỳ, Vấn đáp, Trắc nghiệm
    seat_number = Column(String(50), nullable=True)  # e.g. "042"
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="exams")
    course = relationship("Course", back_populates="exams")

    __table_args__ = (
        Index("idx_exam_user_date", "user_id", "exam_date"),
    )
