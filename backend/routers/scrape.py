"""
POST /api/v1/scrape      — Nhận URL, tạo job, trigger background task
GET  /api/v1/scrape/status/{job_id} — Polling trạng thái
"""

from __future__ import annotations
import asyncio
import logging
import re
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..db import crud
from ..db.models import Review
from ..models.schemas import ScrapeRequest, ScrapeJobResponse, ScrapeStatusResponse
from ..services.scraper import scrape_restaurant
from ..services.similarity import compute_simhash, find_clusters
from ..services.content_module import analyze_content
from ..services.behavior_module import analyze_behavior, ReviewMeta
from ..services.trust_engine import build_trust_result, generate_risk_report, build_timeline
from ..ml.model import get_classifier

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scrape", tags=["scrape"])

MODEL_VERSION = "phobert_reviewtrust_v1"


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[àáạảãâầấậẩẫăằắặẳẵ]", "a", text)
    text = re.sub(r"[èéẹẻẽêềếệểễ]", "e", text)
    text = re.sub(r"[ìíịỉĩ]", "i", text)
    text = re.sub(r"[òóọỏõôồốộổỗơờớợởỡ]", "o", text)
    text = re.sub(r"[ùúụủũưừứựửữ]", "u", text)
    text = re.sub(r"[ỳýỵỷỹ]", "y", text)
    text = re.sub(r"[đ]", "d", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text[:200]


async def _run_scrape_pipeline(job_id: str, url: str, max_reviews: int):
    """Background task: scrape → analyze → lưu DB."""
    # Tạo DB session mới cho background task
    from ..db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            await crud.update_scrape_job(db, job_id, status="processing", progress=5)

            async def progress_cb(pct: int, msg: str):
                await crud.update_scrape_job(db, job_id, progress=pct, message=msg)

            # 1. Scrape
            scraped = await scrape_restaurant(url, max_reviews, progress_callback=progress_cb)
            if not scraped or not scraped.reviews:
                await crud.update_scrape_job(
                    db, job_id, status="failed",
                    error_message="Không scrape được reviews. Google Maps có thể đang chặn."
                )
                return

            await crud.update_scrape_job(db, job_id, progress=50, message="Đang lưu dữ liệu...")

            # 2. Upsert restaurant
            slug = _slugify(scraped.name)
            restaurant = await crud.get_restaurant_by_slug(db, slug)
            if not restaurant:
                restaurant = await crud.create_restaurant(
                    db,
                    name=scraped.name,
                    slug=slug,
                    address=scraped.address,
                    google_place_id=scraped.google_place_id,
                    google_maps_url=url,
                )
            await crud.update_restaurant_scraped_at(db, restaurant.id)

            # 3. Lưu reviews
            reviews_data = []
            for r in scraped.reviews:
                simhash = compute_simhash(r.content)
                reviews_data.append({
                    "restaurant_id": restaurant.id,
                    "content": r.content,
                    "star_rating": r.star_rating,
                    "reviewer_name": r.reviewer_name,
                    "reviewer_review_count": r.reviewer_review_count,
                    "posted_relative": r.posted_relative,
                    "posted_at": r.posted_at,
                    "simhash": simhash,
                    "source": "google_maps",
                })
            db_reviews = await crud.bulk_create_reviews(db, reviews_data)

            await crud.update_scrape_job(db, job_id, progress=60, message="Đang phân tích reviews...")

            # 4. Analyze pipeline
            classifier = get_classifier()
            batch_texts = [r.content for r in scraped.reviews]
            batch_meta = [
                ReviewMeta(
                    review_id=db_reviews[i].id,
                    reviewer_name=scraped.reviews[i].reviewer_name,
                    reviewer_review_count=scraped.reviews[i].reviewer_review_count,
                    posted_at=scraped.reviews[i].posted_at,
                    star_rating=scraped.reviews[i].star_rating,
                )
                for i in range(len(scraped.reviews))
            ]

            scores_data = []
            for i, (db_review, raw_review) in enumerate(zip(db_reviews, scraped.reviews)):
                other_texts = batch_texts[:i] + batch_texts[i+1:]
                content_result = analyze_content(
                    raw_review.content,
                    raw_review.star_rating,
                    classifier,
                    batch_texts=other_texts,
                )
                behavior_result = analyze_behavior(batch_meta[i], batch_meta)
                trust = build_trust_result(content_result, behavior_result)

                scores_data.append({
                    "review_id": db_review.id,
                    "content_score": trust.content_score,
                    "behavior_score": trust.behavior_score,
                    "trust_score": trust.trust_score,
                    "confidence": trust.confidence,
                    "content_only": False,
                    "badge": trust.badge,
                    "aspects_found": trust.aspects_found,
                    "explanation": trust.explanation,
                    "breakdown": trust.breakdown,
                    "model_version": MODEL_VERSION,
                })

                if i % 10 == 0:
                    progress = 60 + int((i / len(db_reviews)) * 35)
                    await crud.update_scrape_job(
                        db, job_id, progress=progress,
                        message=f"Đang phân tích {i+1}/{len(db_reviews)} reviews..."
                    )

            await crud.bulk_create_trust_scores(db, scores_data)

            await crud.update_scrape_job(
                db, job_id,
                status="done",
                progress=100,
                message="Hoàn tất!",
                restaurant_id=restaurant.id,
                restaurant_slug=slug,
                reviews_scraped=len(db_reviews),
            )
            logger.info(f"Job {job_id} done: {len(db_reviews)} reviews for {scraped.name}")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            await crud.update_scrape_job(
                db, job_id, status="failed",
                error_message=str(e)[:500]
            )


@router.post("", response_model=ScrapeJobResponse, status_code=202)
async def start_scrape(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    if "google.com/maps" not in request.url and "maps.app.goo" not in request.url:
        raise HTTPException(400, "URL không hợp lệ. Phải là Google Maps URL.")

    job_id = str(uuid.uuid4())
    await crud.create_scrape_job(db, job_id, request.url)

    background_tasks.add_task(
        _run_scrape_pipeline, job_id, request.url, request.max_reviews
    )

    return ScrapeJobResponse(
        job_id=job_id,
        status="pending",
        message="Đang khởi tạo scrape job...",
    )


@router.get("/status/{job_id}", response_model=ScrapeStatusResponse)
async def get_scrape_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    job = await crud.get_scrape_job(db, job_id)
    if not job:
        raise HTTPException(404, "Job không tìm thấy")

    return ScrapeStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        restaurant_slug=job.restaurant_slug,
        restaurant_name=None,
        reviews_scraped=job.reviews_scraped if job.status == "done" else None,
    )
