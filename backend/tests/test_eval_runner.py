from app.core.db import SessionLocal
from app.models.dataset import Dataset, DatasetItem
from app.models.evaluation import EvalRun
from app.models.project import Project
from app.models.prompt import PromptVersion
from app.models.user import User
from app.services.eval_runner import run_evaluation


def test_run_evaluation_with_mock_provider(client):
    """The mock provider should let a full run complete and produce metrics."""
    db = SessionLocal()
    try:
        user = User(email="runner@example.com", hashed_password="x")
        db.add(user)
        db.flush()
        project = Project(name="RAG Bot", task_type="rag", owner_id=user.id)
        db.add(project)
        db.flush()
        prompt = PromptVersion(project_id=project.id, version=1, content="Be accurate.")
        ds = Dataset(project_id=project.id, name="qa", version=1, row_count=20)
        db.add_all([prompt, ds])
        db.flush()
        for i in range(20):
            db.add(
                DatasetItem(
                    dataset_id=ds.id,
                    question=f"Question number {i}: explain concept {i}?",
                    ground_truth=f"Ground truth for {i}",
                )
            )
        run = EvalRun(
            project_id=project.id,
            dataset_id=ds.id,
            prompt_version_id=prompt.id,
            name="baseline",
            config={"model": "gpt-4.1", "temperature": 0.2, "retriever": "hybrid", "top_k": 5},
        )
        db.add(run)
        db.commit()
        run_id = run.id
    finally:
        db.close()

    db = SessionLocal()
    try:
        result = run_evaluation(run_id, db)
        assert result.status == "completed"
        assert 0.0 < result.accuracy <= 1.0
        assert result.avg_latency_ms > 0
        assert result.total_tokens > 0
        assert result.total_cost_usd > 0
        assert 0.0 <= result.retrieval_precision <= 1.0
        assert len(result.results) == 20
    finally:
        db.close()


def test_model_choice_changes_outcomes(client):
    """Different models should yield different (deterministic) accuracy — powers Compare."""
    db = SessionLocal()
    try:
        user = User(email="cmp@example.com", hashed_password="x")
        db.add(user)
        db.flush()
        project = Project(name="Cmp", task_type="rag", owner_id=user.id)
        db.add(project)
        db.flush()
        ds = Dataset(project_id=project.id, name="qa", version=1, row_count=50)
        db.add(ds)
        db.flush()
        for i in range(50):
            db.add(DatasetItem(dataset_id=ds.id, question=f"q{i}", ground_truth=f"a{i}"))
        runs = {}
        for model in ["gpt-4.1", "llama"]:
            run = EvalRun(
                project_id=project.id,
                dataset_id=ds.id,
                config={"model": model, "temperature": 0.2, "retriever": "hybrid", "top_k": 5},
            )
            db.add(run)
            db.flush()
            runs[model] = run.id
        db.commit()
    finally:
        db.close()

    accuracies = {}
    for model, rid in runs.items():
        db = SessionLocal()
        try:
            accuracies[model] = run_evaluation(rid, db).accuracy
        finally:
            db.close()

    # The higher-quality model should generally score higher on 50 examples.
    assert accuracies["gpt-4.1"] > accuracies["llama"]
