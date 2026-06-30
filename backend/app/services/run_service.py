"""Helpers for creating and triggering evaluation runs."""
from app.core.config import settings
from app.models.evaluation import EvalRun

# Metrics where a higher value is better (used to interpret comparison deltas).
HIGHER_IS_BETTER = {
    "accuracy": True,
    "faithfulness": True,
    "retrieval_precision": True,
    "hallucination_rate": False,
    "toxicity_rate": False,
    "avg_latency_ms": False,
    "total_cost_usd": False,
}


def trigger_run(run_id: int) -> None:
    """Dispatch the evaluation: async via Celery if a broker is configured,
    otherwise run it synchronously in-process."""
    from app.workers.tasks import run_evaluation_task

    if settings.celery_eager:
        run_evaluation_task(run_id)  # runs inline
    else:
        run_evaluation_task.delay(run_id)


def compute_deltas(a: EvalRun, b: EvalRun) -> list[dict]:
    metrics = [
        "accuracy",
        "faithfulness",
        "hallucination_rate",
        "toxicity_rate",
        "retrieval_precision",
        "avg_latency_ms",
        "total_cost_usd",
    ]
    deltas = []
    for m in metrics:
        av = getattr(a, m)
        bv = getattr(b, m)
        delta = round(bv - av, 6)
        if delta == 0:
            direction = "flat"
        else:
            improved = (delta > 0) == HIGHER_IS_BETTER[m]
            direction = "up" if improved else "down"
        deltas.append({"metric": m, "a": av, "b": bv, "delta": delta, "direction": direction})
    return deltas
