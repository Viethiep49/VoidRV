"""
Identity Module — Layer 2: Nhận diện danh tính reviewer.

Signals (không cần vào profile):
  1. Review count (từ card)
  2. Writing effort (length × aspect)
  3. Specificity (tên món, giá, nhân viên)
  4. Experience markers (regex)
  5. Emotion authenticity (mixed = thật)
  6. Stylometry (TF-IDF char n-grams → farm detection)
  7. Vietnamese spam patterns
  → Reviewer Archetype classification
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .aspect_extractor import extract_aspects

# ── Vietnamese spam templates ────────────────────────────────────────────────

FARM_TEMPLATES = [
    "ngon lắm", "sẽ quay lại", "recommend", "5 sao",
    "tuyệt vời", "nhân viên nhiệt tình", "không gian đẹp",
    "giá cả hợp lý", "sẽ ủng hộ", "10 điểm", "quán ngon",
    "đáng để thử", "rất hài lòng", "chất lượng tốt",
]

# ── Positive / Negative words for emotion check ─────────────────────────────

POSITIVE_WORDS = {
    "ngon", "tuyệt", "xuất sắc", "tốt", "thích", "đỉnh", "xịn",
    "hài lòng", "thơm", "tươi", "chất lượng", "recommend",
}
NEGATIVE_WORDS = {
    "dở", "tệ", "thất vọng", "không ngon", "chán", "nguội", "mặn",
    "đắt", "chậm", "thô lỗ", "bẩn", "phàn nàn",
}

# ── Experience marker patterns ───────────────────────────────────────────────

EXPERIENCE_PATTERNS = [
    (r"lần (thứ|đầu|\d+)", "lần ghé"),
    (r"hôm (qua|nay|trước)", "thời gian cụ thể"),
    (r"đi với (gia đình|bạn|người yêu|đồng nghiệp)", "đi cùng ai"),
    (r"đặt (món|qua app|grab|shopee)", "đặt hàng"),
    (r"ngồi (tầng|bàn|ngoài|trong)", "vị trí ngồi"),
    (r"chờ (\d+|mấy) (phút|tiếng)", "thời gian chờ"),
]

# ── Specificity patterns ────────────────────────────────────────────────────

DISH_PATTERN = re.compile(
    r"phở|bún|cơm|bánh|chả|gỏi|lẩu|mì|hủ tiếu|bò kho|canh|"
    r"nem|chè|xôi|cháo|sushi|pizza|burger|steak|salad",
    re.IGNORECASE,
)
PRICE_PATTERN = re.compile(r"\d+\s*k|\d+\.\d+|\d+\s*(nghìn|đồng|vnđ|vnd)", re.IGNORECASE)
STAFF_PATTERN = re.compile(r"nhân viên|chị|anh|bạn phục vụ|chủ quán|bếp trưởng", re.IGNORECASE)


def _review_count_bonus(count: int | None) -> tuple[int, str | None]:
    if count is None:
        return 0, None
    if count >= 20:
        return 15, f"✓ Reviewer có {count} bài đánh giá (Foodie)"
    if count >= 5:
        return 5, f"✓ Reviewer có {count} bài đánh giá"
    if count >= 3:
        return 0, None
    return -15, f"⚠ Ghost account — chỉ có {count} bài đánh giá"


def _writing_effort(word_count: int, aspect_count: int) -> int:
    return min(10, word_count // 10 + aspect_count * 2)


def _specificity_bonus(text: str) -> tuple[int, list[str]]:
    found: list[str] = []
    if DISH_PATTERN.search(text):
        found.append("tên món")
    if PRICE_PATTERN.search(text):
        found.append("giá tiền")
    if STAFF_PATTERN.search(text):
        found.append("nhân viên")
    bonus = min(15, len(found) * 5)
    return bonus, found


def _experience_markers(text: str) -> tuple[int, list[str]]:
    text_lower = text.lower()
    found: list[str] = []
    for pattern, label in EXPERIENCE_PATTERNS:
        if re.search(pattern, text_lower):
            found.append(label)
    bonus = min(10, len(found) * 5)
    return bonus, found


def _emotion_authenticity(text: str) -> tuple[int, float]:
    text_lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    total = pos + neg
    if total == 0:
        return 0, 0.5

    ratio = min(pos, neg) / total
    if ratio > 0.2:
        return 10, round(ratio, 2)  # Mixed emotions = authentic
    words = len(text.split())
    if ratio == 0 and words >= 20:
        return -5, 0.0  # Hoàn toàn 1 chiều + dài
    return 0, round(ratio, 2)


def _vietnamese_spam_score(text: str) -> tuple[int, int]:
    text_lower = text.lower()
    matches = sum(1 for t in FARM_TEMPLATES if t in text_lower)
    words = len(text.split())

    if words < 15 and matches >= 2:
        return -15, matches
    if words < 10 and matches >= 1:
        return -10, matches

    # Emoji spam check
    emoji_count = len(re.findall(r"[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff]", text))
    if words > 0 and emoji_count / words > 0.5:
        return -5, matches

    return 0, matches


def _stylometry_penalty(
    text: str,
    batch_texts: list[str],
) -> tuple[int, float]:
    """
    TF-IDF character 3-grams → cosine similarity vs batch.
    Detect cùng farm worker viết nhiều review.
    """
    if not batch_texts or len(batch_texts) < 2:
        return 0, 0.0

    all_texts = [text] + batch_texts
    try:
        vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=(3, 3),
            max_features=5000,
        )
        tfidf = vectorizer.fit_transform(all_texts)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:])[0]
        max_sim = float(max(sims)) if len(sims) > 0 else 0.0
    except Exception:
        return 0, 0.0

    if max_sim > 0.85:
        return -20, round(max_sim, 3)
    if max_sim > 0.70:
        return -10, round(max_sim, 3)
    return 0, round(max_sim, 3)


# ── Reviewer Archetypes ──────────────────────────────────────────────────────

ARCHETYPE_FOODIE = "foodie"
ARCHETYPE_CASUAL = "casual"
ARCHETYPE_NEWBIE = "newbie"
ARCHETYPE_GHOST = "ghost"
ARCHETYPE_FARM = "farm"


def classify_archetype(
    review_count: int | None,
    identity_score: float,
    word_count: int,
    stylometry_sim: float,
    in_burst: bool,
) -> str:
    # Farm suspect: style trùng hoặc (burst + ghost + template)
    if stylometry_sim > 0.70:
        return ARCHETYPE_FARM
    if in_burst and (review_count or 999) <= 2 and identity_score < 35:
        return ARCHETYPE_FARM

    rc = review_count or 0
    if rc >= 20 and identity_score >= 75 and word_count >= 30:
        return ARCHETYPE_FOODIE
    if 5 <= rc <= 19 and identity_score >= 50:
        return ARCHETYPE_CASUAL
    if rc < 5 and identity_score >= 40:
        return ARCHETYPE_NEWBIE
    if rc <= 2 and identity_score < 40:
        return ARCHETYPE_GHOST

    return ARCHETYPE_CASUAL  # default


# ── Main function ────────────────────────────────────────────────────────────

@dataclass
class IdentityResult:
    identity_score: float
    reviewer_archetype: str
    review_count_bonus: int = 0
    writing_effort: int = 0
    specificity_bonus: int = 0
    specificity_found: list[str] = field(default_factory=list)
    experience_bonus: int = 0
    experience_markers: list[str] = field(default_factory=list)
    emotion_bonus: int = 0
    emotion_ratio: float = 0.0
    stylometry_penalty: int = 0
    stylometry_max_sim: float = 0.0
    vn_spam_penalty: int = 0
    vn_spam_matches: int = 0
    explanation: list[str] = field(default_factory=list)


def analyze_identity(
    text: str,
    review_count: int | None,
    batch_texts: list[str] | None = None,
    in_burst: bool = False,
) -> IdentityResult:
    """
    Phân tích Identity Score cho 1 review.

    Args:
        text: Nội dung review
        review_count: Số review tổng của reviewer (từ card)
        batch_texts: Các review khác trong batch để so stylometry
        in_burst: Review này có nằm trong burst day không
    """
    base = 50
    explanation: list[str] = []

    # 1. Review count
    rc_bonus, rc_msg = _review_count_bonus(review_count)
    if rc_msg:
        explanation.append(rc_msg)

    # 2. Writing effort
    words = text.split()
    word_count = len(words)
    aspects = extract_aspects(text)
    effort = _writing_effort(word_count, len(aspects))
    if effort >= 8:
        explanation.append(f"✓ Review chi tiết, bỏ công viết ({word_count} từ, {len(aspects)} aspect)")

    # 3. Specificity
    spec_bonus, spec_found = _specificity_bonus(text)
    if spec_found:
        explanation.append(f"✓ Đề cập cụ thể: {', '.join(spec_found)}")
    elif word_count >= 10:
        explanation.append("⚠ Không đề cập chi tiết cụ thể (tên món, giá, nhân viên)")

    # 4. Experience markers
    exp_bonus, exp_found = _experience_markers(text)
    if exp_found:
        explanation.append(f"✓ Dấu hiệu trải nghiệm thực: {', '.join(exp_found)}")

    # 5. Emotion authenticity
    emo_bonus, emo_ratio = _emotion_authenticity(text)
    if emo_bonus > 0:
        explanation.append("✓ Review có cả khen lẫn chê — cảm xúc thực tế")
    elif emo_bonus < 0:
        explanation.append("⚠ Review hoàn toàn 1 chiều — ít tự nhiên")

    # 6. Stylometry
    style_pen, style_sim = _stylometry_penalty(text, batch_texts or [])
    if style_pen <= -20:
        explanation.append(f"⚠ Văn phong trùng lặp cao với review khác (similarity {style_sim:.0%}) — nghi farm")
    elif style_pen <= -10:
        explanation.append(f"⚠ Văn phong tương tự review khác (similarity {style_sim:.0%})")

    # 7. Vietnamese spam
    vn_pen, vn_matches = _vietnamese_spam_score(text)
    if vn_pen < 0:
        explanation.append(f"⚠ Chứa {vn_matches} mẫu câu review farm phổ biến")

    # Positive summary
    if not explanation:
        explanation.append("✓ Không phát hiện dấu hiệu bất thường về danh tính")

    # Total score
    raw = (
        base
        + rc_bonus
        + effort
        + spec_bonus
        + exp_bonus
        + emo_bonus
        + style_pen
        + vn_pen
    )
    score = round(max(0.0, min(100.0, raw)), 1)

    # Archetype
    archetype = classify_archetype(review_count, score, word_count, style_sim, in_burst)

    return IdentityResult(
        identity_score=score,
        reviewer_archetype=archetype,
        review_count_bonus=rc_bonus,
        writing_effort=effort,
        specificity_bonus=spec_bonus,
        specificity_found=spec_found,
        experience_bonus=exp_bonus,
        experience_markers=exp_found,
        emotion_bonus=emo_bonus,
        emotion_ratio=emo_ratio,
        stylometry_penalty=style_pen,
        stylometry_max_sim=style_sim,
        vn_spam_penalty=vn_pen,
        vn_spam_matches=vn_matches,
        explanation=explanation,
    )
