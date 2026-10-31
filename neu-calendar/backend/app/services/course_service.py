from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundException
from app.models.course import Course
from app.models.semester import Semester
from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate, CourseUpdate


class CourseService:
    def __init__(self, db: Session):
        self.course_repo = CourseRepository(db)

    def get_current_semester(self) -> Optional[Semester]:
        return self.course_repo.get_current_semester()

    def get_all_semesters(self) -> List[Semester]:
        return self.course_repo.get_all_semesters()

    def get_courses(self, semester_id: Optional[int] = None) -> List[Course]:
        return self.course_repo.get_all_courses(semester_id)

    def get_course(self, course_id: int) -> Course:
        course = self.course_repo.get_by_id(course_id)
        if not course:
            raise NotFoundException("Môn học không tồn tại")
        return course

    def create_course(self, req: CourseCreate) -> Course:
        course = Course(
            code=req.code.strip().upper(),
            name=req.name.strip(),
            credits=req.credits,
            lecturer=req.lecturer.strip() if req.lecturer else None,
            semester_id=req.semester_id,
        )
        return self.course_repo.create(course)

    def update_course(self, course_id: int, req: CourseUpdate) -> Course:
        course = self.get_course(course_id)
        if req.code is not None:
            course.code = req.code.strip().upper()
        if req.name is not None:
            course.name = req.name.strip()
        if req.credits is not None:
            course.credits = req.credits
        if req.lecturer is not None:
            course.lecturer = req.lecturer.strip()
        if req.semester_id is not None:
            course.semester_id = req.semester_id
        return self.course_repo.update(course)

    def delete_course(self, course_id: int) -> None:
        course = self.get_course(course_id)
        self.course_repo.delete(course)
