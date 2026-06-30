from datetime import datetime

from pydantic import BaseModel, Field


class PromptCreate(BaseModel):
    content: str = Field(min_length=1)
    notes: str = ""


class PromptOut(BaseModel):
    id: int
    project_id: int
    version: int
    content: str
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}
