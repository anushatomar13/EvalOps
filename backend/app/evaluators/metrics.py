from dataclasses import dataclass
from typing import List

from app.models.evaluation import EvalResult


@dataclass
class AggregateMetrics:
    accuracy: float = 0.0
    faithfulness: float = 0.0
    hallucination_rate: float = 0.0
    toxicity_rate: float = 0.0
    retrieval_precision: float = 0.0
    avg_latency_ms: float = 0.0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    failures: int = 0


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def aggregate(results: List[EvalResult], retrieval_scores: List[float]) -> AggregateMetrics:
    """Roll per-example results up into the headline run metrics."""
    if not results:
        return AggregateMetrics()

    n = len(results)
    failures = sum(1 for r in results if r.error)
    scored = [r for r in results if not r.error]

    return AggregateMetrics(
        accuracy=round(sum(1 for r in scored if r.is_correct) / n, 4),
        faithfulness=round(_mean([r.faithfulness for r in scored]), 4),
        hallucination_rate=round(sum(1 for r in scored if r.is_hallucination) / n, 4),
        toxicity_rate=round(_mean([r.toxicity for r in scored]), 4),
        retrieval_precision=round(_mean(retrieval_scores), 4) if retrieval_scores else 0.0,
        avg_latency_ms=round(_mean([r.latency_ms for r in scored]), 1),
        total_tokens=sum(r.tokens for r in results),
        total_cost_usd=round(sum(r.cost_usd for r in results), 6),
        failures=failures,
    )
