"""
Content Module — phân tích nội dung review.

Pipeline:
  1. PhoBERT inference → genuine_prob, confidence
  2. Sentiment vs star check
  3. Aspect extraction
  4. Vocabulary richness (TTR)
  5. Length check
  6. SimHash duplicate check vs batch
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field

from ..ml.model import ReviewClassifier
from .aspect_extractor import extract_aspects, aspect_bonus
from .similarity import find_duplicate_similarity

# ── Sentiment keywords (rule-based) ───────────────────────────────────────────

POSITIVE_WORDS = {
    "ngon", "tuyệt", "xuất sắc", "tốt", "thích", "yêu", "đỉnh", "xịn",
    "hài lòng", "hấp dẫn", "thơm", "tươi", "chất lượng", "recommend",
    "quay lại", "ủng hộ", "5 sao", "5 star",
}
NEGATIVE_WORDS = {
    "dở", "tệ", "thất vọng", "không ngon", "chán", "hôi", "nguội", "mặn",
    "đắt", "chậm", "thô lỗ", "vô lễ", "bẩn", "không về", "không quay lại",
    "phàn nàn", "khiếu nại",
}


def _detect_sentiment(text: str) -> str:
    """
    Đơn giản hóa: rule-based sentiment (positive / negative / neutral).
    Không train thêm model — đủ dùng cho penalty check.
    """
    text_lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"


def _sentiment_penalty(sentiment: str, star: int) -> int:
    if sentiment == "positive" and star <= 2:
        return -25
    if sentiment == "negative" and star >= 4:
        return -25
    return 0


def _length_penalty(word_count: int, aspects: list[str]) -> int:
    if word_count < 10:
        return -30
    if word_count < 20:
        return -20
    if word_count >= 50 and aspects:
        return 5
    return 0


def _ttr_score(text: str) -> tuple[float, int]:
    """
    Type-Token Ratio: unique_words / total_words.
    Returns (ttr, penalty).
    """
    words = text.lower().split()
    if len(words) < 5:
        return 0.0, 0
    ttr = len(set(words)) / len(words)
    penalty = 0
    if ttr < 0.4 and len(words) >= 15:
        penalty = -10   # Template-like
    elif ttr >= 0.7 and len(words) >= 30:
        penalty = 5     # Rich vocabulary
    return ttr, penalty


def _duplicate_penalty(max_sim: float) -> int:
    if max_sim > 0.9:
        return -40
    if max_sim > 0.8:
        return -30
    return 0


@dataclass
class ContentResult:
    content_score: float
    genuine_prob: float
    confidence: float
    sentiment: str
    sentiment_penalty: int
    aspects: list[str] = field(default_factory=list)
    aspect_bonus: int = 0
    ttr: float = 0.0
    ttr_penalty: int = 0
    word_count: int = 0
    length_penalty: int = 0
    max_similarity: float = 0.0
    match_count: int = 0
    duplicate_penalty: int = 0
    explanation: list[str] = field(default_factory=list)


def analyze_content(
    text: str,
    star_rating: int,
    classifier: ReviewClassifier,
    batch_texts: list[str] | None = None,
) -> ContentResult:
    """
    Phân tích nội dung một review.

    Args:
        text: Nội dung review
        star_rating: Số sao (1–5)
        classifier: ReviewClassifier instance
        batch_texts: Các review khác trong cùng quán để check duplicate
    """
    # 1. PhoBERT
    genuine_prob, confidence = classifier.predict(text)
    base_score = genuine_prob * 100

    # 2. Sentiment
    sentiment = _detect_sentiment(text)
    sent_pen = _sentiment_penalty(sentiment, star_rating)

    # 3. Aspects
    aspects = extract_aspects(text)
    asp_bonus = aspect_bonus(aspects)

    # 4. TTR
    ttr, ttr_pen = _ttr_score(text)

    # 5. Length
    words = text.split()
    word_count = len(words)
    len_pen = _length_penalty(word_count, aspects)

    # 6. Duplicate
    max_sim, match_count = 0.0, 0
    if batch_texts:
        max_sim, match_count = find_duplicate_similarity(text, batch_texts)
    dup_pen = _duplicate_penalty(max_sim)

    # Final score
    raw = base_score + sent_pen + asp_bonus + ttr_pen + len_pen + dup_pen
    score = round(max(0.0, min(100.0, raw)), 1)

    # Explanation
    explanation: list[str] = []
    prob_pct = round(genuine_prob * 100, 1)
    conf_pct = round(confidence * 100, 1)

    if genuine_prob >= 0.7:
        explanation.append(f"✓ PhoBERT: {prob_pct}% xác suất là review thật (độ chắc chắn {conf_pct}%)")
    else:
        explanation.append(f"⚠ PhoBERT: {prob_pct}% xác suất là review thật (độ chắc chắn {conf_pct}%)")

    if sent_pen < 0:
        explanation.append(f"⚠ Sentiment {'tích cực' if sentiment == 'positive' else 'tiêu cực'} mâu thuẫn với {star_rating} sao")
    elif sentiment != "neutral":
        explanation.append(f"✓ Sentiment {'tích cực' if sentiment == 'positive' else 'tiêu cực'} khớp với {star_rating} sao")

    if aspects:
        explanation.append(f"✓ Đề cập {len(aspects)} khía cạnh: {', '.join(aspects)}")
    else:
        explanation.append("⚠ Không đề cập khía cạnh cụ thể nào (đồ ăn, dịch vụ, giá...)")

    if ttr_pen < 0:
        explanation.append(f"⚠ Từ vựng lặp lại nhiều (TTR={ttr:.2f}) — có thể là review template")
    elif ttr_pen > 0:
        explanation.append(f"✓ Từ vựng phong phú (TTR={ttr:.2f})")

    if len_pen < 0:
        explanation.append(f"⚠ Review quá ngắn ({word_count} từ)")
    elif len_pen > 0:
        explanation.append(f"✓ Review chi tiết ({word_count} từ)")

    if dup_pen <= -40:
        explanation.append(f"⚠ Nội dung gần giống {match_count} review khác trong quán (copy-paste)")
    elif dup_pen <= -30:
        explanation.append(f"⚠ Nội dung tương tự {match_count} review khác trong quán")

    return ContentResult(
        content_score=score,
        genuine_prob=round(genuine_prob, 4),
        confidence=round(confidence, 4),
        sentiment=sentiment,
        sentiment_penalty=sent_pen,
        aspects=aspects,
        aspect_bonus=asp_bonus,
        ttr=round(ttr, 3),
        ttr_penalty=ttr_pen,
        word_count=word_count,
        length_penalty=len_pen,
        max_similarity=round(max_sim, 3),
        match_count=match_count,
        duplicate_penalty=dup_pen,
        explanation=explanation,
    )
