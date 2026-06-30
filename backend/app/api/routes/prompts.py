from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_owned_project
from app.core.db import get_db
from app.models.project import Project
from app.models.prompt import PromptVersion
from app.schemas.prompt import PromptCreate, PromptOut

router = APIRouter()


@router.post("/projects/{project_id}/prompts", response_model=PromptOut, status_code=201)
def create_prompt_version(
    payload: PromptCreate,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
):
    # Auto-increment version number within the project.
    last = (
        db.query(func.max(PromptVersion.version))
        .filter(PromptVersion.project_id == project.id)
        .scalar()
    )
    version = (last or 0) + 1
    prompt = PromptVersion(
        project_id=project.id, version=version, content=payload.content, notes=payload.notes
    )
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt


@router.get("/projects/{project_id}/prompts", response_model=list[PromptOut])
def list_prompt_versions(
    project: Project = Depends(get_owned_project), db: Session = Depends(get_db)
):
    return (
        db.query(PromptVersion)
        .filter(PromptVersion.project_id == project.id)
        .order_by(PromptVersion.version.desc())
        .all()
    )


@router.get("/projects/{project_id}/prompts/{version}", response_model=PromptOut)
def get_prompt_version(
    version: int,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
):
    prompt = (
        db.query(PromptVersion)
        .filter(PromptVersion.project_id == project.id, PromptVersion.version == version)
        .first()
    )
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    return prompt
