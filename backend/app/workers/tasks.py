from app.core.db import SessionLocal
from app.workers.celery_app import celery_app


@celery_app.task(name="evalforge.run_evaluation")
def run_evaluation_task(run_id: int):
    """Celery entrypoint for executing an evaluation run.

    Opens its own DB session (workers run in separate processes) and delegates
    to the shared runner so sync and async paths share identical logic.
    """
    from app.services.eval_runner import run_evaluation

    db = SessionLocal()
    try:
        run = run_evaluation(run_id, db)
        return {"run_id": run_id, "status": run.status}
    finally:
        db.close()
