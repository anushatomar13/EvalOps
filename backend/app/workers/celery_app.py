from celery import Celery

from app.core.config import settings

# When REDIS_URL is empty we run tasks eagerly (in-process, synchronous), so the
# platform works with no broker. Set REDIS_URL to switch to real async workers.
broker = settings.REDIS_URL or "memory://"
backend = settings.REDIS_URL or "cache+memory://"

celery_app = Celery("evalforge", broker=broker, backend=backend)
celery_app.conf.update(
    task_always_eager=settings.celery_eager,
    task_eager_propagates=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

# Ensure task modules are registered.
celery_app.autodiscover_tasks(["app.workers"])
import app.workers.tasks  # noqa: E402,F401
