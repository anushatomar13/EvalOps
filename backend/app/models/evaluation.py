from sqlalchemy import String, Text, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class EvalRun(Base, TimestampMixin):
    """A single evaluation job: runs a config over a dataset and scores it."""

    __tablename__ = "eval_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    prompt_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("prompt_versions.id"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), default="")
    # queued | running | completed | failed
    status: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    error: Mapped[str] = mapped_column(Text, default="")

    # Frozen snapshot of the system config used for this run.
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    # Optional git commit / CI metadata.
    git_commit: Mapped[str] = mapped_column(String(64), default="")

    # Aggregate metrics (filled in when the run completes).
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    faithfulness: Mapped[float] = mapped_column(Float, default=0.0)
    hallucination_rate: Mapped[float] = mapped_column(Float, default=0.0)
    toxicity_rate: Mapped[float] = mapped_column(Float, default=0.0)
    retrieval_precision: Mapped[float] = mapped_column(Float, default=0.0)
    avg_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    failures: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="runs")
    dataset: Mapped["Dataset"] = relationship(back_populates="runs")
    prompt_version: Mapped["PromptVersion"] = relationship(back_populates="runs")
    results: Mapped[list["EvalResult"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class EvalResult(Base):
    """Per-example result within an evaluation run."""

    __tablename__ = "eval_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("eval_runs.id"), index=True)
    item_id: Mapped[int | None] = mapped_column(ForeignKey("dataset_items.id"), nullable=True)

    question: Mapped[str] = mapped_column(Text)
    ground_truth: Mapped[str] = mapped_column(Text, default="")
    answer: Mapped[str] = mapped_column(Text, default="")

    # LLM-as-a-judge verdict
    is_correct: Mapped[bool] = mapped_column(default=False)
    judge_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    judge_reasoning: Mapped[str] = mapped_column(Text, default="")

    # Per-example metrics
    faithfulness: Mapped[float] = mapped_column(Float, default=0.0)
    is_hallucination: Mapped[bool] = mapped_column(default=False)
    toxicity: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    # Retrieved documents for RAG (JSON list of strings).
    retrieved_docs: Mapped[list] = mapped_column(JSON, default=list)
    error: Mapped[str] = mapped_column(Text, default="")

    run: Mapped["EvalRun"] = relationship(back_populates="results")
