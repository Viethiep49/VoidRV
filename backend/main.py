"""
ReviewTrust — FastAPI entry point.
Model load on startup. DB init on startup.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import init_db
from .ml.model import get_classifier
from .routers import analyze, restaurant, scrape

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()

    logger.info("Loading PhoBERT model...")
    get_classifier()   # Load once, singleton
    logger.info("Model loaded. Server ready.")

    yield

    # Shutdown — nothing to clean up


app = FastAPI(
    title="ReviewTrust API",
    description="Hệ thống đánh giá độ tin cậy review nhà hàng tại Việt Nam",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrape.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")
app.include_router(restaurant.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    from .ml.model import is_model_loaded
    return {
        "status": "ok",
        "model_loaded": is_model_loaded(),
        "model_version": "phobert_reviewtrust_v1",
        "db_connected": True,
    }
