from datetime import datetime
from pydantic import BaseModel, HttpUrl, field_validator


# ── Scrape ────────────────────────────────────────────────────────────────────

class ScrapeRequest(BaseModel):
    url: str
    max_reviews: int = 100

    @field_validator("max_reviews")
    @classmethod
    def cap_max(cls, v: int) -> int:
        return min(v, 200)


class ScrapeJobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class ScrapeStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str | None = None
    restaurant_slug: str | None = None
    restaurant_name: str | None = None
    reviews_scraped: int | None = None


# ── Analyze (demo mode) ───────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    content: str
    star_rating: int

    @field_validator("star_rating")
    @classmethod
    def valid_star(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("star_rating phải từ 1 đến 5")
        return v

    @field_validator("content")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content không được để trống")
        return v.strip()


class ContentBreakdown(BaseModel):
    phobert_genuine_prob: float
    confidence: float
    sentiment_penalty: int
    aspects_found: list[str]
    aspect_bonus: int
    ttr: float
    ttr_penalty: int
    length_words: int
    length_penalty: int
    is_duplicate: bool
    duplicate_similarity: float
    duplicate_penalty: int


class BehaviorBreakdown(BaseModel):
    reviewer_review_count: int | None
    review_count_penalty: int
    frequency_penalty: int
    rating_pattern_penalty: int
    burst_penalty: int


class AnalyzeResponse(BaseModel):
    trust_score: float
    confidence: float
    badge: str
    badge_label: str
    badge_color: str
    content_only: bool
    caveat: str | None = None
    breakdown: dict
    aspects_found: list[str]
    explanation: list[str]


# ── Restaurant dashboard ──────────────────────────────────────────────────────

class ReviewOut(BaseModel):
    id: int
    content: str
    star_rating: int
    reviewer_name: str | None
    reviewer_review_count: int | None
    posted_at: datetime | None
    trust_score: float
    confidence: float | None
    badge: str
    content_only: bool
    aspects_found: list[str]
    explanation: list[str]
    breakdown: dict | None


class TimelinePoint(BaseModel):
    date: str          # "2026-02-15"
    count: int
    is_burst: bool


class SuspiciousCluster(BaseModel):
    cluster_id: int
    review_ids: list[int]
    similarity: float
    sample_content: str


class RiskReport(BaseModel):
    risk_level: str    # cao | trung_binh | thap
    suspicious_ratio: float
    new_account_ratio: float
    suspicious_clusters: int
    risk_factors: list[str]


class RestaurantStats(BaseModel):
    total_reviews: int
    avg_trust_score: float
    avg_star_rating: float
    distribution: dict[str, float]


class RestaurantOut(BaseModel):
    id: int
    name: str
    slug: str
    address: str | None
    google_place_id: str | None
    last_scraped_at: datetime | None


class RestaurantDashboard(BaseModel):
    restaurant: RestaurantOut
    stats: RestaurantStats
    risk_report: RiskReport
    timeline: list[TimelinePoint]
    suspicious_clusters: list[SuspiciousCluster]
    reviews: list[ReviewOut]


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    db_connected: bool
