"""FastAPI application for the Chain Processor system."""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.router import api_router
from .core.config import settings
from chain_processor_core.exceptions.errors import ChainProcessorError

# Import to ensure nodes are registered
import chain_processor_core

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Log the available nodes
available_nodes = chain_processor_core.default_registry.list_nodes()
logger.info(f"Available nodes in registry: {available_nodes}")

app = FastAPI(
    title="Chain Processor API",
    description="API for the Chain Processor system",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.exception_handler(ChainProcessorError)
async def chain_processor_exception_handler(
    request: Request, exc: ChainProcessorError
) -> JSONResponse:
    """Handle Chain Processor specific errors."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "healthy"}
