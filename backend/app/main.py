import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.core.config import settings
from app.core.db import Base, engine
from app.core.metrics import HTTP_LATENCY, HTTP_REQUESTS
import app.models  # noqa: F401  (register models on Base.metadata)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For local/dev convenience we create tables on startup.
    # Production uses Alembic migrations instead.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Continuous Evaluation, Observability & CI/CD for AI Systems",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def track_metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    # Use the route template (not the raw path) to keep label cardinality low.
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)
    HTTP_LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
    HTTP_REQUESTS.labels(request.method, path, response.status_code).inc()
    return response


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME, "env": settings.ENVIRONMENT}


@app.get("/metrics", tags=["system"])
def metrics():
    """Prometheus scrape endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# API routers are registered in app.api.router (added in later steps).
from app.api.router import api_router  # noqa: E402

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
