from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RunConfig(BaseModel):
    model: str = "gpt-4.1"
    temperature: float = 0.2
    embedding: str = "bge-large"
    retriever: str = "hybrid"  # hybrid | dense | sparse
    chunk_size: int = 512
    top_k: int = 5


class RunCreate(BaseModel):
    dataset_id: int
    prompt_version: int | None = None  # version number within the project
    name: str = ""
    config: RunConfig = Field(default_factory=RunConfig)
    git_commit: str = ""


class RunOut(BaseModel):
    id: int
    project_id: int
    dataset_id: int
    prompt_version_id: int | None
    name: str
    status: str
    error: str
    config: dict[str, Any]
    git_commit: str
    accuracy: float
    faithfulness: float
    hallucination_rate: float
    toxicity_rate: float
    retrieval_precision: float
    avg_latency_ms: float
    total_tokens: int
    total_cost_usd: float
    failures: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ResultOut(BaseModel):
    id: int
    question: str
    ground_truth: str
    answer: str
    is_correct: bool
    judge_confidence: float
    judge_reasoning: str
    faithfulness: float
    is_hallucination: bool
    toxicity: float
    latency_ms: float
    tokens: int
    cost_usd: float
    retrieved_docs: list
    error: str

    model_config = {"from_attributes": True}


class MetricDelta(BaseModel):
    metric: str
    a: float
    b: float
    delta: float
    # "up" / "down" / "flat" — direction of B relative to A
    direction: str


class CompareOut(BaseModel):
    run_a: RunOut
    run_b: RunOut
    deltas: list[MetricDelta]
