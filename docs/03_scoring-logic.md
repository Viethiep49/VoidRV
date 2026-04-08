# VoidRV — Scoring Logic chi tiết (3 Layers)

---

## 1. Layer 1: Content Score (0–100) — trọng số 40%

### 1.1 PhoBERT Fake Detection (base score)

- Model: `vinai/phobert-base` fine-tuned cho binary classification (genuine vs fake)
- Input: review text (tokenized, max 256 tokens)
- Output: `genuine_probability` (0–1), `confidence` (max của 2 class softmax)
- `base_score = genuine_probability × 100`

### 1.2 Sentiment vs Star Rating

| Tình huống | Penalty |
|------------|---------|
| Text tích cực + star 1–2 | -25 |
| Text tiêu cực + star 4–5 | -25 |
| Text trung tính / khớp | 0 |

### 1.3 Aspect Extraction

| Aspect | Từ khoá mẫu |
|--------|-------------|
| Đồ ăn | phở, bánh mì, cơm, ngon, dở, tươi, nguội... |
| Dịch vụ | nhân viên, phục vụ, thái độ, chờ lâu... |
| Giá cả | `\d+k`, rẻ, mắc, đắt, hợp lý... |
| Không gian | đẹp, sạch, ồn, thoáng, hẹp... |
| Vị trí | gần, xa, đường, quận, dễ tìm, đỗ xe... |

| Kết quả | Điểm |
|---------|------|
| ≥ 3 aspects | +15 |
| 2 aspects | +10 |
| 1 aspect | 0 |
| 0 aspects | -15 |

### 1.4 Vocabulary Richness — TTR

```python
ttr = len(set(words)) / len(words)
```

| Điều kiện | Điểm |
|-----------|------|
| TTR < 0.4 AND ≥ 15 từ | -10 (template) |
| TTR ≥ 0.7 AND ≥ 30 từ | +5 (rich) |

### 1.5 Length Check

| Điều kiện | Điểm |
|-----------|------|
| < 10 từ | -30 |
| 10–19 từ | -20 |
| 20–49 từ | 0 |
| ≥ 50 từ + có aspect | +5 |

### 1.6 SimHash Copy-paste

| Similarity | Điểm |
|-----------|------|
| > 90% | -40 |
| 80–90% | -30 |
| < 80% | 0 |

Cluster ≥ 3 reviews similarity > 80% → đánh dấu "nhóm nghi ngờ".

### 1.7 Tổng hợp

```python
content_score = clamp(
    base_score + sentiment_pen + aspect_bonus + ttr_pen + length_pen + dup_pen,
    0, 100
)
```

---

## 2. Layer 2: Identity Score (0–100) — trọng số 30%

### 2.1 Review Count (từ card)

| Điều kiện | Điểm |
|-----------|------|
| ≥ 20 reviews | +15 (Foodie) |
| 5–19 reviews | +5 (Casual) |
| 3–4 reviews | 0 |
| < 3 reviews | -15 (Ghost) |

### 2.2 Writing Effort

```python
effort = min(10, word_count // 10 + len(aspects) * 2)
```

Review dài + nhiều aspect = người bỏ công viết → đáng tin hơn.

### 2.3 Specificity Detection

| Signal | Regex pattern | Điểm |
|--------|--------------|------|
| Tên món cụ thể | `phở\|bún\|cơm\|bánh\|chả\|gỏi\|lẩu` | +5 |
| Giá cụ thể | `\d+k\|\d+\.\d+\|\d+ nghìn\|\d+ đồng` | +5 |
| Nhân viên/người | `nhân viên\|chị\|anh\|bạn phục vụ` | +5 |

Max +15 (có cả 3). Đề cập chi tiết = đã thật sự đến quán.

### 2.4 Experience Markers

| Pattern | Ví dụ |
|---------|-------|
| `lần (thứ\|đầu\|\d+)` | "lần thứ 3 ghé" |
| `hôm (qua\|nay\|trước)` | "hôm qua tôi đi" |
| `đi với (gia đình\|bạn)` | "đi với gia đình" |
| `đặt (món\|qua app)` | "đặt qua GrabFood" |
| `ngồi (tầng\|bàn\|ngoài)` | "ngồi tầng 2" |

Mỗi marker match → +5, max +10.

### 2.5 Emotion Authenticity

```python
pos_count = count_positive(text)
neg_count = count_negative(text)
total = pos_count + neg_count
ratio = min(pos_count, neg_count) / total if total > 0 else 0.5
```

| Kết quả | Điểm |
|---------|------|
| Mixed emotions (ratio > 0.2) | +10 |
| Hoàn toàn 1 chiều + dài | -5 |

Review thật: "Phở ngon nhưng chờ lâu." Review giả: "Tuyệt vời! 5 sao! Quay lại!"

### 2.6 Stylometry — Farm Detection

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 3))
tfidf_matrix = vectorizer.fit_transform(batch_texts)
similarity_matrix = cosine_similarity(tfidf_matrix)
```

| Similarity | Điểm |
|-----------|------|
| Max cosine > 0.85 | -20 (cùng farm worker) |
| Max cosine 0.7–0.85 | -10 |
| < 0.7 | 0 (unique style) |

### 2.7 Vietnamese Spam Patterns

```python
FARM_TEMPLATES = [
    "ngon lắm", "sẽ quay lại", "recommend", "5 sao",
    "tuyệt vời", "nhân viên nhiệt tình", "không gian đẹp",
    "giá cả hợp lý", "sẽ ủng hộ", "10 điểm",
]
```

| Điều kiện | Điểm |
|-----------|------|
| < 15 từ + ≥ 2 template phrases | -15 |
| < 10 từ + ≥ 1 template phrase | -10 |
| Emoji ratio > 0.5 | -5 |

### 2.8 Tổng hợp Identity Score

```python
identity_score = clamp(
    50  # neutral start
    + review_count_bonus
    + writing_effort
    + specificity_bonus
    + experience_bonus
    + emotion_bonus
    + stylometry_penalty
    + vn_spam_penalty,
    0, 100
)
```

### 2.9 Reviewer Archetypes

| Archetype | Điều kiện |
|-----------|-----------|
| **Foodie thật** | review_count ≥ 20 AND identity_score ≥ 75 AND word_count ≥ 30 |
| **Casual reviewer** | review_count 5–19 AND identity_score ≥ 50 |
| **Newbie** | review_count < 5 AND identity_score ≥ 40 (không template) |
| **Ghost account** | review_count ≤ 2 AND identity_score < 40 |
| **Farm suspect** | stylometry_sim > 0.7 OR (burst + ghost + template) |

---

## 3. Layer 3: Context Score (0–100) — trọng số 30%

### 3.1 Burst Detection

```python
daily_counts = Counter(r.posted_at.date() for r in batch)
avg = mean(daily_counts.values())
burst_ratio = max_day_count / avg
```

| Điều kiện | Penalty |
|-----------|---------|
| Burst ratio > 5x AND > 10 reviews mới | -25 |
| > 10 new accounts cùng ngày | -20 |
| 5–10 new accounts cùng ngày | -10 |

### 3.2 Rating Pattern

| Điều kiện | Penalty |
|-----------|---------|
| ≥ 10 reviews liên tiếp cùng sao | -15 |
| > 80% là 5★ (batch ≥ 20) | -10 |
| > 80% là 1★ (review bombing) | -10 |

### 3.3 Rating Distribution Forensics

```python
from scipy.stats import chisquare

# Phân bố tự nhiên nhà hàng VN
expected = [0.05, 0.05, 0.10, 0.25, 0.55]  # 1★ → 5★
observed = [stars.count(i) / total for i in range(1, 6)]
stat, p_value = chisquare(observed, expected)
```

| p-value | Penalty |
|---------|---------|
| < 0.01 | -15 (phân bố rất bất thường) |
| < 0.05 | -10 |
| ≥ 0.05 | 0 (phân bố tự nhiên) |

### 3.4 Cross-Platform Gap (Google Maps vs Foody)

| So sánh | Điểm |
|---------|------|
| Rating gap < 0.5★ | +15 (đồng thuận) |
| Rating gap 0.5–1.0★ | 0 |
| Rating gap > 1.0★ | -25 (nghi ngờ cao) |
| GG reviews / Foody reviews > 10x | -15 (inflated volume) |
| Không tìm thấy Foody | -5 (không verify được) |
| Cả 2 đồng thuận (rating + sentiment) | +20 bonus |

### 3.5 Trust Decay (Recency)

```python
def recency_weight(posted_at):
    days = (now - posted_at).days
    if days < 90:   return 1.0
    if days < 180:  return 0.9
    if days < 365:  return 0.75
    return 0.5
```

Dùng trong Adjusted Rating, không penalty trực tiếp.

### 3.6 Tổng hợp Context Score

```python
context_score = clamp(
    100
    + burst_penalty
    + rating_pattern_penalty
    + distribution_penalty
    + cross_platform_bonus_or_penalty,
    0, 100
)
```

---

## 4. Trust Score, Void Score, Adjusted Rating

### Trust Score

```python
# Mode 1 — Batch scrape
trust_score = 0.40 * content_score + 0.30 * identity_score + 0.30 * context_score

# Mode 2 — Demo nhập tay (partial identity, no context)
trust_score = 0.60 * content_score + 0.40 * identity_score_partial
```

### Void Score

```python
void_score = 100 - trust_score
```

### Badge

| Score | Badge | Màu |
|-------|-------|-----|
| ≥ 75 | Đáng tin cậy | Xanh (#22c55e) |
| 50–74 | Cần thận trọng | Vàng (#eab308) |
| < 50 | Nghi ngờ | Đỏ (#ef4444) |

### Adjusted Rating

```python
def adjusted_rating(reviews, trust_scores):
    trusted = [
        (r.star_rating, recency_weight(r.posted_at))
        for r, t in zip(reviews, trust_scores)
        if t >= 50
    ]
    if not trusted:
        return None
    total_weight = sum(w for _, w in trusted)
    return sum(star * w for star, w in trusted) / total_weight
```

→ Rating thực tế ước tính, loại review nghi ngờ, weight theo recency.

---

## 5. Restaurant Risk Report

```python
{
    "risk_level": "cao",           # cao / trung_binh / thap
    "void_score_avg": 34,
    "adjusted_rating": 3.9,        # vs Google Maps 4.8
    "google_rating": 4.8,
    "foody_rating": 3.7,
    "cross_platform_gap": 1.1,
    "suspicious_ratio": 0.31,
    "new_account_ratio": 0.28,
    "suspicious_clusters": 4,
    "burst_dates": ["2026-02-15"],
    "archetype_distribution": {
        "foodie": 0.23,
        "casual": 0.41,
        "newbie": 0.14,
        "ghost": 0.15,
        "farm": 0.07
    },
    "top_trusted_reviews": [12, 45, 67, 89, 102],
    "risk_factors": [
        "31% reviews bị đánh dấu 'Nghi ngờ'",
        "28% reviews từ tài khoản ≤ 2 bài đánh giá",
        "Chênh lệch Google Maps vs Foody: 1.1 sao",
        "Phát hiện 4 nhóm copy-paste",
        "Đợt burst 47 reviews ngày 15/02/2026"
    ],
    "traveler_summary": "Quán có chất lượng khá theo trusted reviews. Rating Google Maps bị đẩy lên ~0.9★. Nên đọc top trusted reviews thay vì tin rating tổng."
}
```
