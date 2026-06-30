from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_owned_project
from app.core.db import get_db
from app.models.dataset import Dataset
from app.models.evaluation import EvalResult, EvalRun
from app.models.project import Project
from app.models.prompt import PromptVersion
from app.schemas.run import CompareOut, ResultOut, RunCreate, RunOut
from app.services.run_service import compute_deltas, trigger_run

router = APIRouter()


def _get_run(db: Session, project: Project, run_id: int) -> EvalRun:
    run = db.get(EvalRun, run_id)
    if run is None or run.project_id != project.id:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("/projects/{project_id}/runs", response_model=RunOut, status_code=201)
def create_run(
    payload: RunCreate,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
):
    dataset = db.get(Dataset, payload.dataset_id)
    if dataset is None or dataset.project_id != project.id:
        raise HTTPException(status_code=400, detail="Dataset not found in this project")

    prompt_version_id = None
    if payload.prompt_version is not None:
        pv = (
            db.query(PromptVersion)
            .filter(
                PromptVersion.project_id == project.id,
                PromptVersion.version == payload.prompt_version,
            )
            .first()
        )
        if pv is None:
            raise HTTPException(status_code=400, detail="Prompt version not found")
        prompt_version_id = pv.id

    run = EvalRun(
        project_id=project.id,
        dataset_id=dataset.id,
        prompt_version_id=prompt_version_id,
        name=payload.name or f"run-{dataset.name}-v{dataset.version}",
        status="queued",
        config=payload.config.model_dump(),
        git_commit=payload.git_commit,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Dispatch (sync in eager mode, async via Celery otherwise).
    trigger_run(run.id)

    db.refresh(run)
    return run


@router.get("/projects/{project_id}/runs", response_model=list[RunOut])
def list_runs(
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
    limit: int = 100,
):
    return (
        db.query(EvalRun)
        .filter(EvalRun.project_id == project.id)
        .order_by(EvalRun.created_at.desc())
        .limit(min(limit, 500))
        .all()
    )


@router.get("/projects/{project_id}/runs/compare", response_model=CompareOut)
def compare_runs(
    a: int = Query(..., description="Run id A (baseline)"),
    b: int = Query(..., description="Run id B (candidate)"),
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
):
    run_a = _get_run(db, project, a)
    run_b = _get_run(db, project, b)
    return CompareOut(run_a=run_a, run_b=run_b, deltas=compute_deltas(run_a, run_b))


@router.get("/projects/{project_id}/runs/{run_id}", response_model=RunOut)
def get_run(
    run_id: int,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
):
    return _get_run(db, project, run_id)


@router.get("/projects/{project_id}/runs/{run_id}/results", response_model=list[ResultOut])
def get_run_results(
    run_id: int,
    project: Project = Depends(get_owned_project),
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    only_failures: bool = False,
):
    run = _get_run(db, project, run_id)
    q = db.query(EvalResult).filter(EvalResult.run_id == run.id)
    if only_failures:
        q = q.filter((EvalResult.is_correct == False) | (EvalResult.error != ""))  # noqa: E712
    return q.offset(offset).limit(min(limit, 500)).all()
