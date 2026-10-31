from datetime import datetime, timedelta, timezone


def test_tasks_crud_and_progress(client):
    # Register & Login
    client.post(
        "/api/v1/auth/register",
        json={"email": "taskuser@neu.edu.vn", "password": "Password123!", "full_name": "Task Tester"}
    )
    tokens = client.post(
        "/api/v1/auth/login",
        json={"email": "taskuser@neu.edu.vn", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Create task
    due = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    res_create = client.post(
        "/api/v1/tasks",
        headers=headers,
        json={
            "title": "Làm bài tập Lập trình Web",
            "description": "Xây dựng backend FastAPI",
            "due_at": due,
            "priority": "high",
            "status": "not_started",
            "progress": 0,
            "estimated_hours": 4.0
        }
    )
    assert res_create.status_code == 201
    task_id = res_create.json()["id"]
    assert res_create.json()["title"] == "Làm bài tập Lập trình Web"

    # List tasks
    res_list = client.get("/api/v1/tasks", headers=headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # Filter tasks by priority
    res_filtered = client.get("/api/v1/tasks?priority=high", headers=headers)
    assert len(res_filtered.json()) == 1
    res_empty = client.get("/api/v1/tasks?priority=low", headers=headers)
    assert len(res_empty.json()) == 0

    # Patch progress
    res_patch = client.patch(
        f"/api/v1/tasks/{task_id}/progress",
        headers=headers,
        json={"progress": 60}
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["progress"] == 60
    assert res_patch.json()["status"] == "in_progress"

    # Complete task
    res_done = client.patch(
        f"/api/v1/tasks/{task_id}/progress",
        headers=headers,
        json={"progress": 100}
    )
    assert res_done.json()["status"] == "done"

    # Delete task
    res_del = client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert res_del.status_code == 204

    # Verify deleted
    res_get = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert res_get.status_code == 404
