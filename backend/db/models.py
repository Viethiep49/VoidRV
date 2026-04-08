from datetime import datetime
from sqlalchemy import (
    BigInteger, Boolean, Float, ForeignKey, Integer,
    SmallInteger, String, Text, DateTime, JSON, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    google_place_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    google_maps_url: Mapped[str | None] = mapped_column(Text)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    reviews: Mapped[list["Review"]] = relationship(back_populates="restaurant")
    scrape_jobs: Mapped[list["ScrapeJob"]] = relationship(back_populates="restaurant")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    star_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    reviewer_name: Mapped[str | None] = mapped_column(String(255))
    reviewer_review_count: Mapped[int | None] = mapped_column(Integer)
    posted_relative: Mapped[str | None] = mapped_column(String(100))  # "3 tuần trước"
    posted_at: Mapped[datetime | None] = mapped_column(DateTime)       # computed
    simhash: Mapped[int | None] = mapped_column(BigInteger)
    source: Mapped[str] = mapped_column(String(50), default="google_maps")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    restaurant: Mapped["Restaurant"] = relationship(back_populates="reviews")
    trust_score: Mapped["TrustScore | None"] = relationship(back_populates="review", uselist=False)


class TrustScore(Base):
    __tablename__ = "trust_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id"), unique=True, nullable=False)
    content_score: Mapped[float] = mapped_column(Float, nullable=False)
    behavior_score: Mapped[float | None] = mapped_column(Float)       # NULL = demo mode
    trust_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)           # PhoBERT confidence
    content_only: Mapped[bool] = mapped_column(Boolean, default=False)
    badge: Mapped[str] = mapped_column(String(20), nullable=False)    # trusted|caution|suspicious
    aspects_found: Mapped[list | None] = mapped_column(JSON)          # ["đồ ăn", "giá cả"]
    explanation: Mapped[list | None] = mapped_column(JSON)            # list of strings
    breakdown: Mapped[dict | None] = mapped_column(JSON)              # detailed signals
    model_version: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    review: Mapped["Review"] = relationship(back_populates="trust_score")


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)    # UUID
    url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    # pending | processing | done | failed
    progress: Mapped[int] = mapped_column(Integer, default=0)         # 0–100
    message: Mapped[str | None] = mapped_column(Text)
    restaurant_id: Mapped[int | None] = mapped_column(ForeignKey("restaurants.id"))
    restaurant_slug: Mapped[str | None] = mapped_column(String(300))
    reviews_scraped: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    restaurant: Mapped["Restaurant | None"] = relationship(back_populates="scrape_jobs")
