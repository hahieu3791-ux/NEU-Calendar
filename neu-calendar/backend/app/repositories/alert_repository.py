from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.alert import Alert


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: int, limit: int = 50) -> List[Alert]:
        return (
            self.db.query(Alert)
            .filter(Alert.user_id == user_id)
            .order_by(Alert.is_read.asc(), Alert.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_unread(self, user_id: int) -> List[Alert]:
        return (
            self.db.query(Alert)
            .filter(Alert.user_id == user_id, Alert.is_read == False)
            .order_by(Alert.created_at.desc())
            .all()
        )

    def get_existing(
        self,
        user_id: int,
        alert_type: str,
        ref_type: Optional[str],
        ref_id: Optional[int]
    ) -> Optional[Alert]:
        """Find an existing alert to avoid duplicates."""
        return (
            self.db.query(Alert)
            .filter(
                Alert.user_id == user_id,
                Alert.type == alert_type,
                Alert.ref_type == ref_type,
                Alert.ref_id == ref_id,
            )
            .first()
        )

    def create(self, alert: Alert) -> Alert:
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_by_id(self, user_id: int, alert_id: int) -> Optional[Alert]:
        return (
            self.db.query(Alert)
            .filter(Alert.user_id == user_id, Alert.id == alert_id)
            .first()
        )

    def mark_as_read(self, user_id: int, alert_id: int) -> Optional[Alert]:
        alert = self.get_by_id(user_id, alert_id)
        if alert:
            alert.is_read = True
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def mark_all_as_read(self, user_id: int) -> int:
        count = (
            self.db.query(Alert)
            .filter(Alert.user_id == user_id, Alert.is_read == False)
            .update({Alert.is_read: True})
        )
        self.db.commit()
        return count

    def delete_by_ref(self, user_id: int, ref_type: str, ref_id: int) -> int:
        """Clear alerts when reference task/exam/class is deleted or resolved."""
        count = (
            self.db.query(Alert)
            .filter(Alert.user_id == user_id, Alert.ref_type == ref_type, Alert.ref_id == ref_id)
            .delete()
        )
        self.db.commit()
        return count
