from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.course import CourseResponse, CourseCreate, CourseUpdate, SemesterResponse
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/current-semester", response_model=Optional[SemesterResponse])
def get_current_semester(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CourseService(db)
    sem = service.get_current_semester()
    if not sem:
        return None
    return SemesterResponse(
        id=sem.id,
        name=sem.name,
        start_date=sem.start_date.isoformat(),
        end_date=sem.end_date.isoformat(),
        is_current=sem.is_current
    )


@router.get("/semesters", response_model=List[SemesterResponse])
def get_semesters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CourseService(db)
    semesters = service.get_all_semesters()
    return [
        SemesterResponse(
            id=s.id,
            name=s.name,
            start_date=s.start_date.isoformat(),
            end_date=s.end_date.isoformat(),
            is_current=s.is_current
        )
        for s in semesters
    ]


@router.get("", response_model=List[CourseResponse])
def get_courses(
    semester_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CourseService(db)
    return service.get_courses(semester_id)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CourseService(db)
    return service.get_course(course_id)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    req: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CourseService(db)
    return service.create_course(req)


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    req: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CourseService(db)
    return service.update_course(course_id, req)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = CourseService(db)
    service.delete_course(course_id)
