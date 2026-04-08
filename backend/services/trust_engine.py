"""
Trust Engine — gộp content + behavior → trust score, badge, report.
"""

from __future__ import annotations
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

from .content_module import ContentResult
from .behavior_module import BehaviorResult
from .similarity import find_clusters

BADGE_TRUSTED = "trusted"
BADGE_CAUTION = "caution"
BADGE_SUSPICIOUS = "suspicious"

BADGE_LABELS = {
    BADGE_TRUSTED: "Đáng tin cậy",
    BADGE_CAUTION: "Cần thận trọng",
    BADGE_SUSPICIOUS: "Nghi ngờ",
}
BADGE_COLORS = {
    BADGE_TRUSTED: "#22c55e",
    BADGE_CAUTION: "#eab308",
    BADGE_SUSPICIOUS: "#ef4444",
}

CONTENT_WEIGHT = 0.6
BEHAVIOR_WEIGHT = 0.4


def compute_trust_score(
    content_score: float,
    behavior_score: float | None,
) -> float:
    if behavior_score is None:
        return round(content_score, 1)
    return round(CONTENT_WEIGHT * content_score + BEHAVIOR_WEIGHT * behavior_score, 1)


def get_badge(score: float) -> str:
    if score >= 75:
        return BADGE_TRUSTED
    if score >= 50:
        return BADGE_CAUTION
    return BADGE_SUSPICIOUS


@dataclass
class TrustResult:
    trust_score: float
    badge: str
    badge_label: str
    badge_color: str
    content_score: float
    behavior_score: float | None
    confidence: float
    content_only: bool
    aspects_found: list[str]
    explanation: list[str]
    breakdown: dict


def build_trust_result(
    content: ContentResult,
    behavior: BehaviorResult | None = None,
) -> TrustResult:
    behavior_score = behavior.behavior_score if behavior else None
    trust_score = compute_trust_score(content.content_score, behavior_score)
    badge = get_badge(trust_score)
    content_only = behavior is None

    # Merge explanation: content first, then behavior
    explanation = list(content.explanation)
    if behavior:
        explanation.extend(behavior.explanation)

    breakdown = {
        "content_score": content.content_score,
        "behavior_score": behavior_score,
        "content_details": {
            "phobert_genuine_prob": content.genuine_prob,
            "confidence": content.confidence,
            "sentiment": content.sentiment,
            "sentiment_penalty": content.sentiment_penalty,
            "aspects_found": content.aspects,
            "aspect_bonus": content.aspect_bonus,
            "ttr": content.ttr,
            "ttr_penalty": content.ttr_penalty,
            "length_words": content.word_count,
            "length_penalty": content.length_penalty,
            "max_similarity": content.max_similarity,
            "match_count": content.match_count,
            "duplicate_penalty": content.duplicate_penalty,
        },
    }
    if behavior:
        breakdown["behavior_details"] = {
            "review_count_penalty": behavior.review_count_penalty,
            "frequency_penalty": behavior.frequency_penalty,
            "rating_pattern_penalty": behavior.rating_pattern_penalty,
            "burst_penalty": behavior.burst_penalty,
            "burst_ratio": behavior.burst_ratio,
        }

    return TrustResult(
        trust_score=trust_score,
        badge=badge,
        badge_label=BADGE_LABELS[badge],
        badge_color=BADGE_COLORS[badge],
        content_score=content.content_score,
        behavior_score=behavior_score,
        confidence=content.confidence,
        content_only=content_only,
        aspects_found=content.aspects,
        explanation=explanation,
        breakdown=breakdown,
    )


# ── Restaurant Risk Report ────────────────────────────────────────────────────

@dataclass
class RestaurantRiskReport:
    risk_level: str             # cao | trung_binh | thap
    suspicious_ratio: float
    new_account_ratio: float
    suspicious_clusters: int
    burst_dates: list[str]      # dates with burst
    risk_factors: list[str]


def generate_risk_report(
    reviews_meta: list[dict],      # list of {review_id, content, reviewer_review_count, posted_at, trust_score}
    trust_scores: list[float],
    texts: list[str],
    review_ids: list[int],
) -> RestaurantRiskReport:
    total = len(trust_scores)
    if total == 0:
        return RestaurantRiskReport(
            risk_level="thap",
            suspicious_ratio=0.0,
            new_account_ratio=0.0,
            suspicious_clusters=0,
            burst_dates=[],
            risk_factors=["Không có đủ dữ liệu để đánh giá"],
        )

    suspicious_count = sum(1 for s in trust_scores if s < 50)
    suspicious_ratio = suspicious_count / total

    new_account_count = sum(
        1 for m in reviews_meta
        if (m.get("reviewer_review_count") or 999) < 3
    )
    new_account_ratio = new_account_count / total

    # Clusters
    clusters = find_clusters(texts, review_ids, threshold=0.8)
    cluster_count = len(clusters)

    # Burst dates
    day_counts: Counter = Counter()
    for m in reviews_meta:
        if m.get("posted_at"):
            d = m["posted_at"]
            if isinstance(d, datetime):
                day_counts[d.date()] += 1
    avg_per_day = sum(day_counts.values()) / len(day_counts) if day_counts else 0
    burst_dates = [
        str(day) for day, count in day_counts.items()
        if avg_per_day > 0 and count / avg_per_day > 4
    ]

    # Risk factors
    risk_factors: list[str] = []
    if suspicious_ratio > 0.15:
        risk_factors.append(f"{round(suspicious_ratio * 100)}% reviews bị đánh dấu 'Nghi ngờ'")
    if new_account_ratio > 0.20:
        risk_factors.append(f"{round(new_account_ratio * 100)}% reviews từ tài khoản ≤ 2 bài đánh giá")
    if cluster_count > 0:
        risk_factors.append(f"Phát hiện {cluster_count} nhóm reviews có nội dung tương tự nhau (copy-paste)")
    if burst_dates:
        risk_factors.append(f"Đợt tăng đột biến reviews vào: {', '.join(burst_dates[:3])}")

    # Risk level
    if suspicious_ratio > 0.30 or cluster_count >= 3 or new_account_ratio > 0.40:
        risk_level = "cao"
    elif suspicious_ratio > 0.15 or cluster_count >= 1 or new_account_ratio > 0.20:
        risk_level = "trung_binh"
    else:
        risk_level = "thap"
        if not risk_factors:
            risk_factors.append("Không phát hiện dấu hiệu bất thường đáng kể")

    return RestaurantRiskReport(
        risk_level=risk_level,
        suspicious_ratio=round(suspicious_ratio, 3),
        new_account_ratio=round(new_account_ratio, 3),
        suspicious_clusters=cluster_count,
        burst_dates=burst_dates,
        risk_factors=risk_factors,
    )


# ── Timeline ──────────────────────────────────────────────────────────────────

def build_timeline(
    reviews_meta: list[dict],
) -> list[dict]:
    """
    Build timeline data cho Recharts.
    Returns list of { date, count, is_burst }.
    """
    day_counts: Counter = Counter()
    for m in reviews_meta:
        if m.get("posted_at") and isinstance(m["posted_at"], datetime):
            day_counts[m["posted_at"].date()] += 1

    if not day_counts:
        return []

    avg = sum(day_counts.values()) / len(day_counts)

    timeline = []
    for day in sorted(day_counts.keys()):
        count = day_counts[day]
        is_burst = avg > 0 and count / avg > 4
        timeline.append({
            "date": str(day),
            "count": count,
            "is_burst": is_burst,
        })

    return timeline
