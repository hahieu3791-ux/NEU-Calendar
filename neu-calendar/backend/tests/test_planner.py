from datetime import datetime, timedelta, timezone, date


def test_ai_planner_generation_and_no_overlap(client, db):
    # Setup user
    client.post(
        "/api/v1/auth/register",
        json={"email": "planuser@neu.edu.vn", "password": "Password123!", "full_name": "Plan Tester"}
    )
    tokens = client.post(
        "/api/v1/auth/login",
        json={"email": "planuser@neu.edu.vn", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Setup course & semester
    from app.models.semester import Semester
    from app.models.course import Course
    sem = Semester(name="Học kỳ I", start_date=date.today(), end_date=date.today() + timedelta(days=90), is_current=True)
    db.add(sem)
    db.flush()
    course = Course(code="IT2010", name="Cấu trúc dữ liệu", credits=3, semester_id=sem.id)
    db.add(course)
    db.commit()

    # Add morning class on Monday (day_of_week=2, 07:00 - 09:30)
    client.post(
        "/api/v1/classes",
        headers=headers,
        json={
            "course_id": course.id,
            "day_of_week": 2,
            "start_period": 1,
            "end_period": 3,
            "room": "A1-502",
            "session_type": "lecture",
            "week_from": 1,
            "week_to": 16
        }
    )

    # Add task
    due = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    client.post(
        "/api/v1/tasks",
        headers=headers,
        json={"title": "Bài tập Cây nhị phân", "due_at": due, "priority": "high", "progress": 0, "course_id": course.id}
    )

    # Generate AI plan
    res_plan = client.post(
        "/api/v1/plans/ai-generate",
        headers=headers,
        json={"days_ahead": 7, "daily_max_hours": 4.0, "include_breaks": True}
    )
    assert res_plan.status_code == 201
    plan_data = res_plan.json()
    assert plan_data["source"] == "ai"
    assert len(plan_data["items"]) > 0

    # Verify no plan item overlaps the class time (07:00 - 09:30)
    for item in plan_data["items"]:
        start_dt = datetime.fromisoformat(item["start_at"])
        # Should not start before 09:30 if on Monday
        # Check start_time
        time_str = start_dt.strftime("%H:%M")
        assert not ("07:00" <= time_str < "09:30")
        assert "ai_reason" in item and len(item["ai_reason"]) > 0

    # Toggle completion of first item
    first_item_id = plan_data["items"][0]["id"]
    res_toggle = client.patch(f"/api/v1/plans/items/{first_item_id}/toggle", headers=headers)
    assert res_toggle.status_code == 200
    assert res_toggle.json()["is_done"] is True
