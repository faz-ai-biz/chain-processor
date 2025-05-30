"""API router for the Chain Processor API."""

from fastapi import APIRouter

from .chains import router as chains_router
from .users import router as users_router
from .nodes import router as nodes_router
from .executions import router as executions_router

api_router = APIRouter()
api_router.include_router(chains_router)
api_router.include_router(users_router)
api_router.include_router(nodes_router)
api_router.include_router(executions_router)


@api_router.get("/ping")
async def ping() -> dict[str, str]:
    """Simple ping endpoint for connectivity checks."""
    return {"message": "pong"}
