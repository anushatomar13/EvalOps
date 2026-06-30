def test_register_login_me(client):
    # Register
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "password": "secret123", "full_name": "Ana"},
    )
    assert r.status_code == 201, r.text
    token = r.json()["access_token"]
    assert token

    # /me with the token
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "ana@example.com"
    assert body["is_admin"] is True  # first user becomes admin

    # Duplicate email rejected
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "ana@example.com", "password": "secret123"},
    )
    assert r.status_code == 400

    # Login (OAuth2 form: username=email)
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "secret123"},
    )
    assert r.status_code == 200
    assert r.json()["access_token"]

    # Wrong password
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "ana@example.com", "password": "wrong"},
    )
    assert r.status_code == 401


def test_me_requires_auth(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401
