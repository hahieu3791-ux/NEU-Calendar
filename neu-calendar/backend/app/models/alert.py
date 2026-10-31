from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # deadline_soon, overdue, exam_soon, conflict
    severity = Column(String(20), default="info", nullable=False)  # info, warning, critical
    message = Column(Text, nullable=False)
    ref_type = Column(String(50), nullable=True)  # task, exam, class_session, plan_item
    ref_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)

    user = relationship("User", back_populates="alerts")

    __table_args__ = (
        Index("idx_alert_user_unread", "user_id", "is_read"),
        Index("idx_alert_dedup", "user_id", "type", "ref_type", "ref_id"),
    )
