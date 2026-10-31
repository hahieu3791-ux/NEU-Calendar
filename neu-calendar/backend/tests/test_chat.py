def test_academic_chat_and_history(client):
    # Setup user
    client.post(
        "/api/v1/auth/register",
        json={"email": "chatuser@neu.edu.vn", "password": "Password123!", "full_name": "Chat Tester"}
    )
    tokens = client.post(
        "/api/v1/auth/login",
        json={"email": "chatuser@neu.edu.vn", "password": "Password123!"}
    ).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Ask question about schedule
    res_chat = client.post(
        "/api/v1/chat",
        headers=headers,
        json={"message": "Hôm nay mình có lịch học gì không?"}
    )
    assert res_chat.status_code == 200
    data = res_chat.json()
    assert "assistant_message" in data
    assert "user_message" in data
    assert len(data["assistant_message"]["content"]) > 0

    # Retrieve history
    res_hist = client.get("/api/v1/chat/history", headers=headers)
    assert res_hist.status_code == 200
    assert len(res_hist.json()) >= 2

    # Clear history
    res_clear = client.delete("/api/v1/chat/history", headers=headers)
    assert res_clear.status_code == 200
    res_hist_after = client.get("/api/v1/chat/history", headers=headers)
    assert len(res_hist_after.json()) == 0
