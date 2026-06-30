import io


def _bootstrap(client, email="runs@example.com"):
    r = client.post("/api/v1/auth/register", json={"email": email, "password": "secret123"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    pid = client.post(
        "/api/v1/projects", json={"name": "Bot", "task_type": "rag"}, headers=h
    ).json()["id"]
    csv_data = "Question,Ground Truth\n" + "\n".join(
        f"What is concept {i}?,Answer {i}" for i in range(15)
    )
    files = {"file": ("qa.csv", io.BytesIO(csv_data.encode()), "text/csv")}
    ds = client.post(
        f"/api/v1/projects/{pid}/datasets",
        data={"name": "qa"},
        files=files,
        headers=h,
    ).json()
    client.post(f"/api/v1/projects/{pid}/prompts", json={"content": "Be accurate."}, headers=h)
    return h, pid, ds["id"]


def test_run_lifecycle_and_results(client):
    h, pid, ds_id = _bootstrap(client)

    # Create run -> runs synchronously in eager mode -> completed
    r = client.post(
        f"/api/v1/projects/{pid}/runs",
        json={
            "dataset_id": ds_id,
            "prompt_version": 1,
            "name": "baseline",
            "config": {"model": "gpt-4.1", "temperature": 0.2, "retriever": "hybrid"},
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    run = r.json()
    assert run["status"] == "completed"
    assert 0 < run["accuracy"] <= 1
    assert run["total_tokens"] > 0
    run_id = run["id"]

    # Per-example results
    results = client.get(
        f"/api/v1/projects/{pid}/runs/{run_id}/results", headers=h
    ).json()
    assert len(results) == 15
    assert "judge_reasoning" in results[0]


def test_compare_runs(client):
    h, pid, ds_id = _bootstrap(client, email="cmp2@example.com")

    def make_run(model):
        return client.post(
            f"/api/v1/projects/{pid}/runs",
            json={"dataset_id": ds_id, "config": {"model": model}},
            headers=h,
        ).json()["id"]

    a = make_run("llama")
    b = make_run("claude")

    r = client.get(
        f"/api/v1/projects/{pid}/runs/compare", params={"a": a, "b": b}, headers=h
    )
    assert r.status_code == 200, r.text
    body = r.json()
    metrics = {d["metric"]: d for d in body["deltas"]}
    assert "accuracy" in metrics
    # Claude (b) should beat llama (a) on accuracy => direction "up"
    assert metrics["accuracy"]["b"] >= metrics["accuracy"]["a"]
