from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine
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


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME, "env": settings.ENVIRONMENT}


# API routers are registered in app.api.router (added in later steps).
from app.api.router import api_router  # noqa: E402

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
