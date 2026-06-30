from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.mixins import TimestampMixin


class PromptVersion(Base, TimestampMixin):
    """An immutable, versioned system/instruction prompt for a project."""

    __tablename__ = "prompt_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    # Auto-incrementing version number within the project (v1, v2, ...).
    version: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    notes: Mapped[str] = mapped_column(Text, default="")

    project: Mapped["Project"] = relationship(back_populates="prompts")
    runs: Mapped[list["EvalRun"]] = relationship(back_populates="prompt_version")
