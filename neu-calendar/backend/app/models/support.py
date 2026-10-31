from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin


class SupportRequest(Base, TimestampMixin):
    __tablename__ = "support_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, in_progress, resolved

    user = relationship("User", back_populates="support_requests")

    __table_args__ = (
        Index("idx_support_user_status", "user_id", "status"),
    )
