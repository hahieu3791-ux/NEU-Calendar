from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.course import Course
from app.models.semester import Semester


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_current_semester(self) -> Optional[Semester]:
        return self.db.query(Semester).filter(Semester.is_current == True).first()

    def get_all_semesters(self) -> List[Semester]:
        return self.db.query(Semester).order_by(Semester.start_date.desc()).all()

    def get_all_courses(self, semester_id: Optional[int] = None) -> List[Course]:
        query = self.db.query(Course)
        if semester_id:
            query = query.filter(Course.semester_id == semester_id)
        return query.order_by(Course.code.asc()).all()

    def get_by_id(self, course_id: int) -> Optional[Course]:
        return self.db.query(Course).filter(Course.id == course_id).first()

    def create(self, course: Course) -> Course:
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def update(self, course: Course) -> Course:
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course: Course) -> None:
        self.db.delete(course)
        self.db.commit()
