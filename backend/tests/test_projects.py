def _auth_headers(client, email="proj@example.com"):
    r = client.post(
        "/api/v1/auth/register", json={"email": email, "password": "secret123"}
    )
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_project_crud_and_prompts(client):
    h = _auth_headers(client)

    # Create
    r = client.post(
        "/api/v1/projects",
        json={"name": "Loan Assistant", "task_type": "rag"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    pid = r.json()["id"]

    # List
    r = client.get("/api/v1/projects", headers=h)
    assert r.status_code == 200 and len(r.json()) == 1

    # Prompt versions auto-increment
    for content in ["v1 prompt", "v2 prompt"]:
        r = client.post(
            f"/api/v1/projects/{pid}/prompts", json={"content": content}, headers=h
        )
        assert r.status_code == 201
    versions = client.get(f"/api/v1/projects/{pid}/prompts", headers=h).json()
    assert [p["version"] for p in versions] == [2, 1]

    # Ownership: another user cannot see it
    h2 = _auth_headers(client, email="other@example.com")
    r = client.get(f"/api/v1/projects/{pid}", headers=h2)
    assert r.status_code == 403
