from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    task_type: str = "rag"  # rag | sql | coding | chat


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    task_type: str | None = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    task_type: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
