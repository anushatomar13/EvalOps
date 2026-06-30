import io


def _setup(client):
    r = client.post(
        "/api/v1/auth/register", json={"email": "ds@example.com", "password": "secret123"}
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    pid = client.post(
        "/api/v1/projects", json={"name": "Finance", "task_type": "rag"}, headers=h
    ).json()["id"]
    return h, pid


def test_csv_upload_and_versioning(client):
    h, pid = _setup(client)
    csv_data = "Question,Ground Truth\nWhat is EMI?,Equated Monthly Installment\nHow is interest calculated?,Principal x rate x time\n"

    files = {"file": ("finance.csv", io.BytesIO(csv_data.encode()), "text/csv")}
    r = client.post(
        f"/api/v1/projects/{pid}/datasets",
        data={"name": "finance", "description": "v1"},
        files=files,
        headers=h,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["version"] == 1 and body["row_count"] == 2

    # Re-upload same name -> version 2
    files = {"file": ("finance.csv", io.BytesIO(csv_data.encode()), "text/csv")}
    r = client.post(
        f"/api/v1/projects/{pid}/datasets",
        data={"name": "finance"},
        files=files,
        headers=h,
    )
    assert r.json()["version"] == 2

    ds_id = body["id"]
    items = client.get(
        f"/api/v1/projects/{pid}/datasets/{ds_id}/items", headers=h
    ).json()
    assert len(items) == 2
    assert items[0]["question"] == "What is EMI?"
    assert items[0]["ground_truth"] == "Equated Monthly Installment"
