from datetime import datetime

from pydantic import BaseModel


class DatasetItemOut(BaseModel):
    id: int
    question: str
    ground_truth: str
    context: str

    model_config = {"from_attributes": True}


class DatasetOut(BaseModel):
    id: int
    project_id: int
    name: str
    version: int
    description: str
    row_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
