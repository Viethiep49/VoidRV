"""
GET /api/v1/restaurant/{slug} — Dashboard: stats + timeline + clusters + reviews.
"""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..db import crud
from ..models.schemas import RestaurantDashboard, ReviewOut, TimelinePoint, SuspiciousCluster
from ..services.similarity import find_clusters
from ..services.trust_engine import generate_risk_report, build_timeline

router = APIRouter(prefix="/restaurant", tags=["restaurant"])


@router.get("/{slug}", response_model=RestaurantDashboard)
async def get_restaurant_dashboard(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    restaurant = await crud.get_restaurant_by_slug(db, slug)
    if not restaurant:
        raise HTTPException(404, "Quán không tìm thấy. Hãy scrape trước.")

    db_reviews = await crud.get_reviews_by_restaurant(db, restaurant.id)
    if not db_reviews:
        raise HTTPException(404, "Quán chưa có reviews. Hãy scrape trước.")

    stats = await crud.get_restaurant_stats(db, restaurant.id)

    # Build data structures
    texts = [r.content for r in db_reviews]
    review_ids = [r.id for r in db_reviews]
    trust_scores = [r.trust_score.trust_score if r.trust_score else 50.0 for r in db_reviews]

    reviews_meta = [
        {
            "review_id": r.id,
            "reviewer_review_count": r.reviewer_review_count,
            "posted_at": r.posted_at,
            "trust_score": r.trust_score.trust_score if r.trust_score else 50.0,
        }
        for r in db_reviews
    ]

    # Risk report
    risk = generate_risk_report(reviews_meta, trust_scores, texts, review_ids)

    # Timeline
    timeline_data = build_timeline(reviews_meta)
    timeline = [TimelinePoint(**t) for t in timeline_data]

    # Suspicious clusters
    raw_clusters = find_clusters(texts, review_ids, threshold=0.8)
    suspicious_clusters = []
    for i, cluster_ids in enumerate(raw_clusters):
        # Tìm content của review đầu tiên trong cluster làm sample
        sample = next((r.content for r in db_reviews if r.id == cluster_ids[0]), "")
        suspicious_clusters.append(
            SuspiciousCluster(
                cluster_id=i + 1,
                review_ids=cluster_ids,
                similarity=0.8,
                sample_content=sample[:150] + "..." if len(sample) > 150 else sample,
            )
        )

    # Reviews list (sorted suspicious first)
    reviews_out = []
    for r in sorted(db_reviews, key=lambda x: (x.trust_score.trust_score if x.trust_score else 50)):
        ts = r.trust_score
        reviews_out.append(
            ReviewOut(
                id=r.id,
                content=r.content,
                star_rating=r.star_rating,
                reviewer_name=r.reviewer_name,
                reviewer_review_count=r.reviewer_review_count,
                posted_at=r.posted_at,
                trust_score=ts.trust_score if ts else 50.0,
                confidence=ts.confidence if ts else None,
                badge=ts.badge if ts else "caution",
                content_only=ts.content_only if ts else True,
                aspects_found=ts.aspects_found or [] if ts else [],
                explanation=ts.explanation or [] if ts else [],
                breakdown=ts.breakdown if ts else None,
            )
        )

    from ..models.schemas import RestaurantOut, RestaurantStats, RiskReport

    return RestaurantDashboard(
        restaurant=RestaurantOut(
            id=restaurant.id,
            name=restaurant.name,
            slug=restaurant.slug,
            address=restaurant.address,
            google_place_id=restaurant.google_place_id,
            last_scraped_at=restaurant.last_scraped_at,
        ),
        stats=RestaurantStats(**stats),
        risk_report=RiskReport(
            risk_level=risk.risk_level,
            suspicious_ratio=risk.suspicious_ratio,
            new_account_ratio=risk.new_account_ratio,
            suspicious_clusters=risk.suspicious_clusters,
            risk_factors=risk.risk_factors,
        ),
        timeline=timeline,
        suspicious_clusters=suspicious_clusters,
        reviews=reviews_out,
    )
