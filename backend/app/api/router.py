from fastapi import APIRouter

api_router = APIRouter()

# Route modules are included here as they are added in later steps.
# e.g. api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
