"""Core evaluation orchestration: run a config over a dataset and score it.

This runs the generate -> judge -> score loop for every dataset item, persists a
per-example EvalResult, then rolls everything up into the run's headline metrics.
Used by both the synchronous path and the Celery worker.
"""
import hashlib

from sqlalchemy.orm import Session

from app.evaluators.metrics import aggregate
from app.models.dataset import DatasetItem
from app.models.evaluation import EvalResult, EvalRun
from app.providers.registry import get_provider, price_per_1k_tokens


def _retrieval_score(question: str, config: dict) -> float:
    """Deterministic mock retrieval precision for RAG configs."""
    retriever = config.get("retriever", "hybrid")
    top_k = int(config.get("top_k", 5))
    h = hashlib.sha256(f"ret|{question}|{retriever}|{top_k}".encode()).hexdigest()
    base = int(h[:8], 16) / 0xFFFFFFFF
    bonus = 0.1 if retriever == "hybrid" else 0.0
    return round(min(1.0, 0.7 + 0.25 * base + bonus), 4)


def run_evaluation(run_id: int, db: Session) -> EvalRun:
    run = db.get(EvalRun, run_id)
    if run is None:
        raise ValueError(f"EvalRun {run_id} not found")

    run.status = "running"
    db.commit()

    try:
        config = dict(run.config or {})
        model = config.get("model", "gpt-4.1")
        config.setdefault("task_type", run.project.task_type)

        system_prompt = ""
        if run.prompt_version is not None:
            system_prompt = run.prompt_version.content
            config["prompt_version"] = f"v{run.prompt_version.version}"

        provider = get_provider(model)
        price = price_per_1k_tokens(model)

        items = (
            db.query(DatasetItem).filter(DatasetItem.dataset_id == run.dataset_id).all()
        )

        results: list[EvalResult] = []
        retrieval_scores: list[float] = []

        for item in items:
            gen = provider.generate(system_prompt, item.question, config)
            cost = round(gen.total_tokens / 1000 * price, 6)

            if gen.error:
                result = EvalResult(
                    run_id=run.id,
                    item_id=item.id,
                    question=item.question,
                    ground_truth=item.ground_truth,
                    error=gen.error,
                    latency_ms=gen.latency_ms,
                )
            else:
                verdict = provider.judge(
                    item.question, item.ground_truth, gen.text, config
                )
                result = EvalResult(
                    run_id=run.id,
                    item_id=item.id,
                    question=item.question,
                    ground_truth=item.ground_truth,
                    answer=gen.text,
                    is_correct=verdict.is_correct,
                    judge_confidence=verdict.confidence,
                    judge_reasoning=verdict.reasoning,
                    faithfulness=verdict.faithfulness,
                    is_hallucination=verdict.is_hallucination,
                    toxicity=verdict.toxicity,
                    latency_ms=gen.latency_ms,
                    tokens=gen.total_tokens,
                    cost_usd=cost,
                    retrieved_docs=gen.retrieved_docs,
                )
                if config.get("task_type") == "rag":
                    retrieval_scores.append(_retrieval_score(item.question, config))

            db.add(result)
            results.append(result)

        db.flush()

        metrics = aggregate(results, retrieval_scores)
        run.accuracy = metrics.accuracy
        run.faithfulness = metrics.faithfulness
        run.hallucination_rate = metrics.hallucination_rate
        run.toxicity_rate = metrics.toxicity_rate
        run.retrieval_precision = metrics.retrieval_precision
        run.avg_latency_ms = metrics.avg_latency_ms
        run.total_tokens = metrics.total_tokens
        run.total_cost_usd = metrics.total_cost_usd
        run.failures = metrics.failures
        run.status = "completed"
        db.commit()
        db.refresh(run)
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        run = db.get(EvalRun, run_id)
        run.status = "failed"
        run.error = str(exc)
        db.commit()
        raise

    return run
