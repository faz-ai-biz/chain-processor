"""API router for the Chain Processor API."""

from fastapi import APIRouter

from .chains import router as chains_router
from .users import router as users_router

router = APIRouter()
router.include_router(chains_router)
router.include_router(users_router)


@router.get("/ping")
async def ping() -> dict[str, str]:
    """Simple ping endpoint for connectivity checks."""
    return {"message": "pong"}
