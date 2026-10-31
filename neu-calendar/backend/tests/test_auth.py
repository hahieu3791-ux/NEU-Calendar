def test_register_and_login(client):
    # Register
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "student1@neu.edu.vn",
            "password": "Password123!",
            "full_name": "Nguyễn Văn A",
            "student_code": "11210001",
            "cohort": "K64",
            "faculty": "Công nghệ thông tin"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "student1@neu.edu.vn"
    assert data["full_name"] == "Nguyễn Văn A"

    # Duplicate register should fail
    res_dup = client.post(
        "/api/v1/auth/register",
        json={
            "email": "student1@neu.edu.vn",
            "password": "Password123!",
            "full_name": "Nguyễn Văn A"
        }
    )
    assert res_dup.status_code == 400

    # Login
    res_login = client.post(
        "/api/v1/auth/login",
        json={"email": "student1@neu.edu.vn", "password": "Password123!"}
    )
    assert res_login.status_code == 200
    tokens = res_login.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Test me
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "student1@neu.edu.vn"

    # Refresh token
    res_ref = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]}
    )
    assert res_ref.status_code == 200
    assert "access_token" in res_ref.json()
