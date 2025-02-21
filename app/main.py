import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.logging_config import configure_logging
from .api.endpoints import posts
from .api.endpoints import vector_store

# Configure logging with both file and console handlers
configure_logging()

logger = logging.getLogger(__name__)
logger.info("Starting LinkedIn Post Generator API...")

app = FastAPI(
    title="LinkedIn Post Generator API",
    description="An async API that generates LinkedIn posts based on provided PDF documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router, prefix="/generate-posts", tags=["posts"])
app.include_router(vector_store.router, prefix="/vector-store", tags=["vector_store"])

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: LinkedIn Post Generator API is now running.")
    # Add additional startup checks

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown: LinkedIn Post Generator API is shutting down.")

logger.info("LinkedIn Post Generator API setup complete.")
