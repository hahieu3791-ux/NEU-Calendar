from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, index=True)  # e.g., IT3080
    name = Column(String(255), nullable=False)  # e.g., Lập trình Web
    credits = Column(Integer, default=3, nullable=False)
    lecturer = Column(String(255), nullable=True)  # e.g., TS. Vũ Đức Long
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False, index=True)

    semester = relationship("Semester", back_populates="courses")
    class_sessions = relationship("ClassSession", back_populates="course", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="course", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="course", cascade="all, delete-orphan")
