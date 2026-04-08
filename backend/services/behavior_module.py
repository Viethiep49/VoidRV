"""
Behavior Module — phân tích hành vi reviewer dựa trên batch context.
Không cần vào profile — dùng review card data + batch analysis.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import Counter


@dataclass
class ReviewMeta:
    """Metadata của 1 review trong batch."""
    review_id: int
    reviewer_name: str | None
    reviewer_review_count: int | None   # Từ card: "X bài đánh giá"
    posted_at: datetime | None
    star_rating: int


@dataclass
class BehaviorResult:
    behavior_score: float
    review_count_penalty: int = 0
    frequency_penalty: int = 0
    rating_pattern_penalty: int = 0
    burst_penalty: int = 0
    burst_ratio: float = 0.0
    explanation: list[str] = field(default_factory=list)


def _review_count_penalty(count: int | None) -> tuple[int, str | None]:
    if count is None:
        return 0, None
    if count < 3:
        return -15, f"⚠ Tài khoản chỉ có {count} bài đánh giá tổng cộng"
    if count < 5:
        return -10, f"⚠ Tài khoản ít kinh nghiệm ({count} bài đánh giá)"
    return 0, f"✓ Tài khoản có {count} bài đánh giá"


def _frequency_penalty(
    target_meta: ReviewMeta,
    batch: list[ReviewMeta],
) -> tuple[int, str | None]:
    """
    Kiểm tra tần suất review của cùng reviewer trong batch.
    Dùng reviewer_name làm key (không có ID).
    """
    if not target_meta.reviewer_name or not target_meta.posted_at:
        return 0, None

    one_hour_ago = target_meta.posted_at - timedelta(hours=1)
    same_reviewer_last_hour = [
        m for m in batch
        if m.reviewer_name == target_meta.reviewer_name
        and m.posted_at
        and one_hour_ago <= m.posted_at <= target_meta.posted_at
        and m.review_id != target_meta.review_id
    ]
    count = len(same_reviewer_last_hour)

    if count > 5:
        return -50, f"⚠ Reviewer đăng {count + 1} reviews trong 1 giờ (bot flag)"
    if count > 3:
        return -40, f"⚠ Reviewer đăng {count + 1} reviews trong 1 giờ"
    if count >= 2:
        return -10, f"⚠ Reviewer đăng {count + 1} reviews trong 1 giờ"
    return 0, None


def _rating_pattern_penalty(
    batch: list[ReviewMeta],
) -> tuple[int, str | None]:
    """
    Kiểm tra phân bố sao trong batch.
    """
    if len(batch) < 10:
        return 0, None

    stars = [m.star_rating for m in batch]
    total = len(stars)
    five_star_count = stars.count(5)
    one_star_count = stars.count(1)

    # Streak liên tiếp
    max_streak = 1
    current_streak = 1
    for i in range(1, len(stars)):
        if stars[i] == stars[i - 1]:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    if max_streak >= 10:
        return -15, f"⚠ {max_streak} reviews liên tiếp cùng loại sao (bất thường)"

    five_ratio = five_star_count / total
    if total >= 20 and five_ratio > 0.80:
        return -10, f"⚠ {round(five_ratio * 100)}% reviews là 5 sao (batch này)"

    one_ratio = one_star_count / total
    if total >= 20 and one_ratio > 0.80:
        return -10, f"⚠ {round(one_ratio * 100)}% reviews là 1 sao (review bombing)"

    return 0, None


def _burst_penalty(
    target_meta: ReviewMeta,
    batch: list[ReviewMeta],
) -> tuple[int, float, str | None]:
    """
    Phát hiện đợt tăng đột biến reviews (burst).
    So sánh số reviews ngày của target với avg ngày.
    """
    if not target_meta.posted_at:
        return 0, 0.0, None

    # Đếm reviews theo ngày trong batch
    day_counts: Counter = Counter()
    for m in batch:
        if m.posted_at:
            day_counts[m.posted_at.date()] += 1

    if len(day_counts) < 3:
        return 0, 0.0, None

    target_day = target_meta.posted_at.date()
    target_day_count = day_counts.get(target_day, 0)
    avg_count = sum(day_counts.values()) / len(day_counts)

    if avg_count == 0:
        return 0, 0.0, None

    burst_ratio = target_day_count / avg_count

    # Count reviewers mới trong ngày target
    new_reviewers_today = sum(
        1 for m in batch
        if m.posted_at
        and m.posted_at.date() == target_day
        and (m.reviewer_review_count or 0) < 3
    )

    if burst_ratio > 5 and target_day_count > 10:
        msg = f"⚠ Đăng trong đợt bùng phát: {target_day_count} reviews ngày {target_day} (bình thường {avg_count:.1f}/ngày)"
        return -25, round(burst_ratio, 1), msg

    if new_reviewers_today > 10:
        msg = f"⚠ Ngày {target_day} có {new_reviewers_today} tài khoản mới đăng review"
        return -20, round(burst_ratio, 1), msg

    if new_reviewers_today >= 5:
        return -10, round(burst_ratio, 1), f"⚠ Ngày {target_day} có {new_reviewers_today} tài khoản mới đăng review"

    return 0, round(burst_ratio, 1), None


def analyze_behavior(
    target: ReviewMeta,
    batch: list[ReviewMeta],
) -> BehaviorResult:
    """
    Phân tích behavior score cho 1 review dựa trên batch context.

    Args:
        target: ReviewMeta của review đang xét
        batch: Tất cả reviews trong quán (bao gồm cả target)
    """
    base_score = 100
    explanation: list[str] = []

    # 1. Review count
    rc_pen, rc_msg = _review_count_penalty(target.reviewer_review_count)
    if rc_msg:
        explanation.append(rc_msg)

    # 2. Frequency
    freq_pen, freq_msg = _frequency_penalty(target, batch)
    if freq_msg:
        explanation.append(freq_msg)

    # 3. Rating pattern
    rat_pen, rat_msg = _rating_pattern_penalty(batch)
    if rat_msg:
        explanation.append(rat_msg)

    # 4. Burst
    burst_pen, burst_ratio, burst_msg = _burst_penalty(target, batch)
    if burst_msg:
        explanation.append(burst_msg)

    # Positive signal
    if not explanation:
        explanation.append("✓ Không phát hiện dấu hiệu bất thường về hành vi")

    raw = base_score + rc_pen + freq_pen + rat_pen + burst_pen
    score = round(max(0.0, min(100.0, raw)), 1)

    return BehaviorResult(
        behavior_score=score,
        review_count_penalty=rc_pen,
        frequency_penalty=freq_pen,
        rating_pattern_penalty=rat_pen,
        burst_penalty=burst_pen,
        burst_ratio=burst_ratio,
        explanation=explanation,
    )
