"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "restaurants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(300), unique=True, nullable=False),
        sa.Column("address", sa.Text()),
        sa.Column("google_place_id", sa.String(100), unique=True),
        sa.Column("google_maps_url", sa.Text()),
        sa.Column("last_scraped_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("restaurant_id", sa.Integer(), sa.ForeignKey("restaurants.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("star_rating", sa.SmallInteger(), nullable=False),
        sa.Column("reviewer_name", sa.String(255)),
        sa.Column("reviewer_review_count", sa.Integer()),
        sa.Column("posted_relative", sa.String(100)),
        sa.Column("posted_at", sa.DateTime()),
        sa.Column("simhash", sa.BigInteger()),
        sa.Column("source", sa.String(50), server_default="google_maps"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_reviews_restaurant_id", "reviews", ["restaurant_id"])

    op.create_table(
        "trust_scores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("review_id", sa.Integer(), sa.ForeignKey("reviews.id"), unique=True, nullable=False),
        sa.Column("content_score", sa.Float(), nullable=False),
        sa.Column("behavior_score", sa.Float()),
        sa.Column("trust_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float()),
        sa.Column("content_only", sa.Boolean(), server_default="false"),
        sa.Column("badge", sa.String(20), nullable=False),
        sa.Column("aspects_found", sa.JSON()),
        sa.Column("explanation", sa.JSON()),
        sa.Column("breakdown", sa.JSON()),
        sa.Column("model_version", sa.String(50)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "scrape_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("progress", sa.Integer(), server_default="0"),
        sa.Column("message", sa.Text()),
        sa.Column("restaurant_id", sa.Integer(), sa.ForeignKey("restaurants.id")),
        sa.Column("restaurant_slug", sa.String(300)),
        sa.Column("reviews_scraped", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("scrape_jobs")
    op.drop_table("trust_scores")
    op.drop_index("ix_reviews_restaurant_id", "reviews")
    op.drop_table("reviews")
    op.drop_table("restaurants")
