from datetime import datetime, timedelta, timezone, date


def test_alerts_generation_and_deduplication(client, db):
    # Setup user
    client.post(
        "/api/v1/auth/register",
        json={"email": "alertuser@neu.edu.vn", "password": "Password123!", "full_name": "Alert Tester"}
    )
    tokens = client.post(
        "/api/v1/auth/login",
        json={"email": "alertuser@neu.edu.vn", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 1. Create a course and semester
    from app.models.semester import Semester
    from app.models.course import Course
    sem = Semester(name="Học kỳ I", start_date=date.today(), end_date=date.today() + timedelta(days=90), is_current=True)
    db.add(sem)
    db.flush()
    course = Course(code="IT101", name="Nhập môn CNTT", credits=3, semester_id=sem.id)
    db.add(course)
    db.commit()

    # 2. Create urgent task (due in 10 hours)
    urgent_due = (datetime.now(timezone.utc) + timedelta(hours=10)).isoformat()
    client.post(
        "/api/v1/tasks",
        headers=headers,
        json={"title": "Nộp bài tập khẩn", "due_at": urgent_due, "priority": "critical", "progress": 0, "course_id": course.id}
    )

    # 3. Create upcoming exam (in 2 days)
    exam_date = (date.today() + timedelta(days=2)).isoformat()
    client.post(
        "/api/v1/exams",
        headers=headers,
        json={"course_id": course.id, "exam_date": exam_date, "start_time": "08:00", "room": "A1-502"}
    )

    # 4. Refresh alerts
    res_refresh = client.post("/api/v1/alerts/refresh", headers=headers)
    assert res_refresh.status_code == 200
    summary = res_refresh.json()
    assert summary["total_unread"] >= 2
    assert summary["critical_count"] >= 2

    # 5. Check deduplication: refresh again, count should not double!
    res_refresh2 = client.post("/api/v1/alerts/refresh", headers=headers)
    assert res_refresh2.status_code == 200
    summary2 = res_refresh2.json()
    assert summary2["total_unread"] == summary["total_unread"]

    # 6. Mark single alert as read
    alerts = client.get("/api/v1/alerts", headers=headers).json()
    alert_id = alerts[0]["id"]
    res_read = client.patch(f"/api/v1/alerts/{alert_id}/read", headers=headers)
    assert res_read.status_code == 200
    assert res_read.json()["is_read"] is True

    # 7. Mark all read
    res_all = client.post("/api/v1/alerts/mark-all-read", headers=headers)
    assert res_all.status_code == 200
    summary3 = client.get("/api/v1/alerts/summary", headers=headers).json()
    assert summary3["total_unread"] == 0
