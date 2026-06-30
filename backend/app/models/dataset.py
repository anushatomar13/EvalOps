from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class Dataset(Base, TimestampMixin):
    """A versioned evaluation dataset (e.g. finance_v1, finance_v2)."""

    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    version: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, default="")
    row_count: Mapped[int] = mapped_column(Integer, default=0)

    project: Mapped["Project"] = relationship(back_populates="datasets")
    items: Mapped[list["DatasetItem"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    runs: Mapped[list["EvalRun"]] = relationship(back_populates="dataset")


class DatasetItem(Base):
    """A single evaluation example: a question and its expected answer."""

    __tablename__ = "dataset_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), index=True)
    question: Mapped[str] = mapped_column(Text)
    ground_truth: Mapped[str] = mapped_column(Text, default="")
    # Optional context for RAG tasks (expected/source documents), JSON-encoded.
    context: Mapped[str] = mapped_column(Text, default="")

    dataset: Mapped["Dataset"] = relationship(back_populates="items")
