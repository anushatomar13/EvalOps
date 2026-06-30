from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_owned_project
from app.core.db import get_db
from app.models.dataset import Dataset, DatasetItem
from app.models.project import Project
from app.schemas.dataset import DatasetItemOut, DatasetOut
from app.services.dataset_service import parse_csv

router = APIRouter()


@router.post("/projects/{project_id}/datasets", status_code=201)
async def upload_dataset(
    name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")
    content = await file.read()
    try:
        rows, warnings = parse_csv(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Version datasets by name within the project (finance_v1, finance_v2, ...).
    last = (
        db.query(func.max(Dataset.version))
        .filter(Dataset.project_id == project.id, Dataset.name == name)
        .scalar()
    )
    version = (last or 0) + 1

    dataset = Dataset(
        project_id=project.id,
        name=name,
        version=version,
        description=description,
        row_count=len(rows),
    )
    db.add(dataset)
    db.flush()  # get dataset.id

    db.bulk_save_objects(
        [DatasetItem(dataset_id=dataset.id, **row) for row in rows]
    )
    db.commit()
    db.refresh(dataset)

    out = DatasetOut.model_validate(dataset).model_dump()
    out["warnings"] = warnings
    return out


@router.get("/projects/{project_id}/datasets", response_model=list[DatasetOut])
def list_datasets(
    project: Project = Depends(get_owned_project), db: Session = Depends(get_db)
):
    return (
        db.query(Dataset)
        .filter(Dataset.project_id == project.id)
        .order_by(Dataset.created_at.desc())
        .all()
    )


@router.get(
    "/projects/{project_id}/datasets/{dataset_id}/items",
    response_model=list[DatasetItemOut],
)
def list_dataset_items(
    dataset_id: int,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
):
    dataset = db.get(Dataset, dataset_id)
    if dataset is None or dataset.project_id != project.id:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return (
        db.query(DatasetItem)
        .filter(DatasetItem.dataset_id == dataset_id)
        .offset(offset)
        .limit(min(limit, 500))
        .all()
    )
