"""
Unit tests cho scoring engine — không cần GPU, không cần DB.
Mock PhoBERT classifier để test logic thuần.
"""

import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from backend.services.content_module import analyze_content, ContentResult
from backend.services.behavior_module import analyze_behavior, ReviewMeta
from backend.services.trust_engine import build_trust_result, compute_trust_score, get_badge
from backend.services.aspect_extractor import extract_aspects, aspect_bonus
from backend.services.similarity import jaccard_similarity, find_clusters


# ── Mock classifier ────────────────────────────────────────────────────────────

def make_classifier(genuine_prob: float = 0.9):
    clf = MagicMock()
    clf.predict.return_value = (genuine_prob, max(genuine_prob, 1 - genuine_prob))
    return clf


# ── Aspect extractor ──────────────────────────────────────────────────────────

class TestAspectExtractor:
    def test_food_detected(self):
        aspects = extract_aspects("Phở rất ngon, thơm lắm")
        assert "đồ ăn" in aspects

    def test_price_pattern_detected(self):
        aspects = extract_aspects("Giá chỉ 25k một tô")
        assert "giá cả" in aspects

    def test_service_detected(self):
        aspects = extract_aspects("Nhân viên phục vụ nhanh và niềm nở")
        assert "dịch vụ" in aspects

    def test_multiple_aspects(self):
        aspects = extract_aspects("Đồ ăn ngon, giá hợp lý, không gian đẹp, nhân viên thân thiện")
        assert len(aspects) >= 3

    def test_generic_review_no_aspects(self):
        aspects = extract_aspects("Tốt lắm")
        assert len(aspects) == 0

    def test_bonus_three_aspects(self):
        aspects = ["đồ ăn", "dịch vụ", "giá cả"]
        assert aspect_bonus(aspects) == 15

    def test_penalty_zero_aspects(self):
        assert aspect_bonus([]) == -15


# ── Content module ────────────────────────────────────────────────────────────

class TestContentModule:
    def test_genuine_review_high_score(self):
        clf = make_classifier(0.9)
        result = analyze_content(
            "Phở bò ngon tuyệt, nước dùng đậm đà, giá 50k hợp lý, nhân viên thân thiện",
            star_rating=5,
            classifier=clf,
        )
        assert result.content_score >= 70
        assert "đồ ăn" in result.aspects

    def test_short_review_penalty(self):
        clf = make_classifier(0.5)
        result = analyze_content("Ngon", star_rating=5, classifier=clf)
        assert result.length_penalty == -30
        assert result.content_score < 60

    def test_sentiment_star_mismatch_penalty(self):
        clf = make_classifier(0.8)
        result = analyze_content(
            "Đồ ăn rất ngon tuyệt vời thích lắm",
            star_rating=1,
            classifier=clf,
        )
        assert result.sentiment_penalty == -25

    def test_duplicate_penalty_high_similarity(self):
        clf = make_classifier(0.8)
        batch = ["Quán ngon lắm, phục vụ tốt, giá hợp lý, sẽ quay lại"] * 5
        result = analyze_content(
            "Quán ngon lắm, phục vụ tốt, giá hợp lý, sẽ quay lại",
            star_rating=5,
            classifier=clf,
            batch_texts=batch,
        )
        assert result.duplicate_penalty < 0

    def test_ttr_template_penalty(self):
        clf = make_classifier(0.7)
        # Từ lặp lại nhiều → TTR thấp
        text = "ngon ngon ngon ngon ngon ngon ngon ngon ngon ngon ngon ngon ngon ngon ngon ngon"
        result = analyze_content(text, star_rating=5, classifier=clf)
        assert result.ttr_penalty == -10

    def test_score_clamped_0_to_100(self):
        clf = make_classifier(0.0)
        result = analyze_content("x", star_rating=1, classifier=clf)
        assert 0 <= result.content_score <= 100


# ── Behavior module ───────────────────────────────────────────────────────────

class TestBehaviorModule:
    def _make_target(self, review_count=10, posted_at=None, star=5):
        return ReviewMeta(
            review_id=1,
            reviewer_name="Nguyen A",
            reviewer_review_count=review_count,
            posted_at=posted_at or datetime.utcnow(),
            star_rating=star,
        )

    def test_new_account_penalty(self):
        target = self._make_target(review_count=1)
        result = analyze_behavior(target, [target])
        assert result.review_count_penalty == -15

    def test_established_account_no_penalty(self):
        target = self._make_target(review_count=20)
        result = analyze_behavior(target, [target])
        assert result.review_count_penalty == 0

    def test_high_frequency_penalty(self):
        now = datetime.utcnow()
        target = ReviewMeta(1, "Nguyen A", 5, now, 5)
        # 6 reviews trong 1 giờ từ cùng reviewer
        batch = [
            ReviewMeta(i, "Nguyen A", 5, now - timedelta(minutes=i * 5), 5)
            for i in range(7)
        ]
        result = analyze_behavior(target, batch)
        assert result.frequency_penalty <= -40

    def test_burst_detection(self):
        now = datetime.utcnow()
        target = ReviewMeta(1, "Nguyen B", 1, now, 5)
        # 15 tài khoản mới cùng ngày
        batch = [
            ReviewMeta(i, f"User{i}", 1, now - timedelta(hours=i % 12), 5)
            for i in range(15)
        ]
        batch.append(target)
        result = analyze_behavior(target, batch)
        assert result.burst_penalty < 0

    def test_diverse_reviews_no_penalty(self):
        target = self._make_target(review_count=50)
        now = datetime.utcnow()
        batch = [
            ReviewMeta(i, f"User{i}", 10, now - timedelta(days=i * 3), i % 5 + 1)
            for i in range(20)
        ]
        result = analyze_behavior(target, batch)
        assert result.behavior_score >= 80


# ── Trust engine ──────────────────────────────────────────────────────────────

class TestTrustEngine:
    def test_badge_trusted(self):
        assert get_badge(80) == "trusted"

    def test_badge_caution(self):
        assert get_badge(60) == "caution"

    def test_badge_suspicious(self):
        assert get_badge(40) == "suspicious"

    def test_score_weighted_combination(self):
        score = compute_trust_score(80, 60)
        assert score == pytest.approx(0.6 * 80 + 0.4 * 60, abs=0.1)

    def test_content_only_mode(self):
        score = compute_trust_score(70, None)
        assert score == 70.0


# ── Similarity ────────────────────────────────────────────────────────────────

class TestSimilarity:
    def test_identical_texts_high_similarity(self):
        text = "Quán ngon lắm, phục vụ tốt, giá hợp lý"
        sim = jaccard_similarity(text, text)
        assert sim > 0.9

    def test_different_texts_low_similarity(self):
        sim = jaccard_similarity(
            "Phở bò ngon đậm đà nước dùng thơm",
            "Pizza hải sản mỏng giòn giá rẻ không gian đẹp",
        )
        assert sim < 0.3

    def test_cluster_detection(self):
        texts = [
            "Quán ngon lắm, phục vụ tốt, giá hợp lý, sẽ quay lại",
            "Quán ngon lắm, phục vụ tốt, giá hợp lý, sẽ quay lại nhé",
            "Quán ngon lắm, phục vụ tốt, giá hợp lý, quay lại ngay",
            "Phở rất ngon đậm đà, nước dùng thơm, nhân viên vui vẻ",
        ]
        ids = [1, 2, 3, 4]
        clusters = find_clusters(texts, ids, threshold=0.7)
        assert len(clusters) >= 1
        assert 1 in clusters[0] or 2 in clusters[0]
