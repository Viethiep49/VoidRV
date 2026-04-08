from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .models import Restaurant, Review, TrustScore, ScrapeJob


# ── Restaurant ────────────────────────────────────────────────────────────────

async def get_restaurant_by_slug(db: AsyncSession, slug: str) -> Restaurant | None:
    result = await db.execute(
        select(Restaurant).where(Restaurant.slug == slug)
    )
    return result.scalar_one_or_none()


async def get_restaurant_by_place_id(db: AsyncSession, place_id: str) -> Restaurant | None:
    result = await db.execute(
        select(Restaurant).where(Restaurant.google_place_id == place_id)
    )
    return result.scalar_one_or_none()


async def create_restaurant(db: AsyncSession, **kwargs) -> Restaurant:
    restaurant = Restaurant(**kwargs)
    db.add(restaurant)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


async def update_restaurant_scraped_at(db: AsyncSession, restaurant_id: int):
    restaurant = await db.get(Restaurant, restaurant_id)
    if restaurant:
        restaurant.last_scraped_at = datetime.utcnow()
        await db.commit()


# ── Review ────────────────────────────────────────────────────────────────────

async def create_review(db: AsyncSession, **kwargs) -> Review:
    review = Review(**kwargs)
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


async def bulk_create_reviews(db: AsyncSession, reviews_data: list[dict]) -> list[Review]:
    reviews = [Review(**data) for data in reviews_data]
    db.add_all(reviews)
    await db.commit()
    return reviews


async def get_reviews_by_restaurant(
    db: AsyncSession, restaurant_id: int
) -> list[Review]:
    result = await db.execute(
        select(Review)
        .where(Review.restaurant_id == restaurant_id)
        .options(selectinload(Review.trust_score))
        .order_by(Review.posted_at.asc())
    )
    return list(result.scalars().all())


async def get_simhashes_by_restaurant(
    db: AsyncSession, restaurant_id: int
) -> list[tuple[int, int]]:
    """Return list of (review_id, simhash) for cross-review duplicate check."""
    result = await db.execute(
        select(Review.id, Review.simhash)
        .where(Review.restaurant_id == restaurant_id)
        .where(Review.simhash.is_not(None))
    )
    return list(result.all())


# ── TrustScore ────────────────────────────────────────────────────────────────

async def create_trust_score(db: AsyncSession, **kwargs) -> TrustScore:
    ts = TrustScore(**kwargs)
    db.add(ts)
    await db.commit()
    await db.refresh(ts)
    return ts


async def bulk_create_trust_scores(db: AsyncSession, scores_data: list[dict]) -> list[TrustScore]:
    scores = [TrustScore(**data) for data in scores_data]
    db.add_all(scores)
    await db.commit()
    return scores


# ── ScrapeJob ─────────────────────────────────────────────────────────────────

async def create_scrape_job(db: AsyncSession, job_id: str, url: str) -> ScrapeJob:
    job = ScrapeJob(id=job_id, url=url, status="pending")
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_scrape_job(db: AsyncSession, job_id: str) -> ScrapeJob | None:
    return await db.get(ScrapeJob, job_id)


async def update_scrape_job(db: AsyncSession, job_id: str, **kwargs):
    job = await db.get(ScrapeJob, job_id)
    if job:
        for k, v in kwargs.items():
            setattr(job, k, v)
        job.updated_at = datetime.utcnow()
        await db.commit()


# ── Dashboard stats ───────────────────────────────────────────────────────────

async def get_restaurant_stats(db: AsyncSession, restaurant_id: int) -> dict:
    result = await db.execute(
        select(
            func.count(TrustScore.id).label("total"),
            func.avg(TrustScore.trust_score).label("avg_trust"),
            func.avg(Review.star_rating).label("avg_star"),
            func.sum(
                func.cast(TrustScore.trust_score >= 75, Integer)
            ).label("trusted_count"),
            func.sum(
                func.cast(
                    (TrustScore.trust_score >= 50) & (TrustScore.trust_score < 75), Integer
                )
            ).label("caution_count"),
            func.sum(
                func.cast(TrustScore.trust_score < 50, Integer)
            ).label("suspicious_count"),
        )
        .join(Review, TrustScore.review_id == Review.id)
        .where(Review.restaurant_id == restaurant_id)
    )
    row = result.one()
    total = row.total or 0
    return {
        "total_reviews": total,
        "avg_trust_score": round(row.avg_trust or 0, 1),
        "avg_star_rating": round(row.avg_star or 0, 1),
        "distribution": {
            "trusted": round((row.trusted_count or 0) / total * 100, 1) if total else 0,
            "caution": round((row.caution_count or 0) / total * 100, 1) if total else 0,
            "suspicious": round((row.suspicious_count or 0) / total * 100, 1) if total else 0,
        },
    }
