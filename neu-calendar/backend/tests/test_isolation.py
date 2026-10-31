from datetime import datetime, timedelta, timezone, date


def test_user_data_isolation(client, db):
    # Register User A
    client.post(
        "/api/v1/auth/register",
        json={"email": "usera@neu.edu.vn", "password": "Password123!", "full_name": "User Alpha"}
    )
    tokens_a = client.post(
        "/api/v1/auth/login",
        json={"email": "usera@neu.edu.vn", "password": "Password123!"}
    ).json()
    headers_a = {"Authorization": f"Bearer {tokens_a['access_token']}"}

    # Register User B
    client.post(
        "/api/v1/auth/register",
        json={"email": "userb@neu.edu.vn", "password": "Password123!", "full_name": "User Beta"}
    )
    tokens_b = client.post(
        "/api/v1/auth/login",
        json={"email": "userb@neu.edu.vn", "password": "Password123!"}
    ).json()
    headers_b = {"Authorization": f"Bearer {tokens_b['access_token']}"}

    # User A creates a task
    due = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    res_task_a = client.post(
        "/api/v1/tasks",
        headers=headers_a,
        json={"title": "Private Task A", "due_at": due, "priority": "high", "progress": 0}
    )
    task_a_id = res_task_a.json()["id"]

    # User B tries to get User A's task -> Must return 404
    res_b_get_a = client.get(f"/api/v1/tasks/{task_a_id}", headers=headers_b)
    assert res_b_get_a.status_code == 404

    # User B tries to delete User A's task -> Must return 404
    res_b_del_a = client.delete(f"/api/v1/tasks/{task_a_id}", headers=headers_b)
    assert res_b_del_a.status_code == 404

    # User B lists tasks -> Must not see User A's task
    res_b_list = client.get("/api/v1/tasks", headers=headers_b)
    assert res_b_list.status_code == 200
    assert len(res_b_list.json()) == 0

    # User A creates a class session
    from app.models.semester import Semester
    from app.models.course import Course
    sem = Semester(name="Học kỳ I", start_date=date.today(), end_date=date.today() + timedelta(days=90), is_current=True)
    db.add(sem)
    db.flush()
    course = Course(code="IT999", name="Bảo mật ứng dụng", credits=3, semester_id=sem.id)
    db.add(course)
    db.commit()

    res_class_a = client.post(
        "/api/v1/classes",
        headers=headers_a,
        json={
            "course_id": course.id,
            "day_of_week": 3,
            "start_period": 1,
            "end_period": 3,
            "room": "B2-101",
            "session_type": "lecture",
            "week_from": 1,
            "week_to": 16
        }
    )
    class_a_id = res_class_a.json()["id"]

    # User B tries to get User A's class -> Must return 404
    res_b_get_class = client.get(f"/api/v1/classes/{class_a_id}", headers=headers_b)
    assert res_b_get_class.status_code == 404
