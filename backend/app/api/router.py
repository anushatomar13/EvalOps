from fastapi import APIRouter

from app.api.routes import auth, datasets, projects, prompts, runs

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(prompts.router, tags=["prompts"])
api_router.include_router(datasets.router, tags=["datasets"])
api_router.include_router(runs.router, tags=["runs"])
