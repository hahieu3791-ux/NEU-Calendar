from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.study_plan import StudyPlan, StudyPlanItem


class StudyPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: int) -> List[StudyPlan]:
        return (
            self.db.query(StudyPlan)
            .options(joinedload(StudyPlan.items))
            .filter(StudyPlan.user_id == user_id)
            .order_by(StudyPlan.start_date.desc())
            .all()
        )

    def get_active(self, user_id: int) -> Optional[StudyPlan]:
        return (
            self.db.query(StudyPlan)
            .options(joinedload(StudyPlan.items))
            .filter(StudyPlan.user_id == user_id, StudyPlan.status == "active")
            .order_by(StudyPlan.created_at.desc())
            .first()
        )

    def get_by_id(self, user_id: int, plan_id: int) -> Optional[StudyPlan]:
        return (
            self.db.query(StudyPlan)
            .options(joinedload(StudyPlan.items))
            .filter(StudyPlan.user_id == user_id, StudyPlan.id == plan_id)
            .first()
        )

    def create(self, plan: StudyPlan) -> StudyPlan:
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def update(self, plan: StudyPlan) -> StudyPlan:
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def delete(self, plan: StudyPlan) -> None:
        self.db.delete(plan)
        self.db.commit()

    def get_item_by_id(self, user_id: int, item_id: int) -> Optional[StudyPlanItem]:
        return (
            self.db.query(StudyPlanItem)
            .join(StudyPlan, StudyPlan.id == StudyPlanItem.plan_id)
            .filter(StudyPlan.user_id == user_id, StudyPlanItem.id == item_id)
            .first()
        )

    def update_item(self, item: StudyPlanItem) -> StudyPlanItem:
        self.db.commit()
        self.db.refresh(item)
        return item
