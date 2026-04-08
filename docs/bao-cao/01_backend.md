# Báo cáo: Backend — ReviewTrust

## 1. Tổng quan

Backend được xây dựng bằng **FastAPI (Python)**, cung cấp REST API cho toàn bộ hệ thống. Chạy async, load PhoBERT model một lần lúc startup, phục vụ mọi request sau đó.

---

## 2. Cấu trúc thư mục

```
backend/
├── main.py                    Entry point, CORS, lifespan (startup/shutdown)
├── db/
│   ├── database.py            SQLAlchemy async engine + session factory
│   ├── models.py              ORM models (4 bảng)
│   └── crud.py                DB operations (create, get, bulk insert, stats)
├── models/
│   └── schemas.py             Pydantic v2 request/response schemas
├── ml/
│   ├── model.py               PhoBERT loader + inference (singleton)
│   └── weights/               .pt file (git-ignored)
├── services/
│   ├── scraper.py             Playwright scraper (Google Maps)
│   ├── content_module.py      Content scoring pipeline
│   ├── behavior_module.py     Behavior scoring pipeline
│   ├── trust_engine.py        Trust score + risk report + timeline
│   ├── aspect_extractor.py    Aspect extraction (5 loại)
│   └── similarity.py          SimHash + cluster detection
├── routers/
│   ├── scrape.py              POST /scrape + GET /scrape/status/{id}
│   ├── analyze.py             POST /analyze (demo mode)
│   └── restaurant.py          GET /restaurant/{slug}
├── tests/
│   └── test_scoring.py        Unit tests (không cần GPU/DB)
└── requirements.txt
```

---

## 3. Database (PostgreSQL + SQLAlchemy async)

### 4 bảng chính

**`restaurants`**
- `slug` (unique): dùng làm URL path (vd: `banh-mi-phuong`)
- `google_place_id`: để tránh scrape cùng quán 2 lần
- `last_scraped_at`: cache 24h — không re-scrape trong vòng 24h

**`reviews`**
- `reviewer_review_count`: lấy từ review card ("X bài đánh giá")
- `posted_relative`: lưu text gốc ("3 tuần trước")
- `posted_at`: convert sang datetime (mất precision nhưng đủ dùng)
- `simhash` (BIGINT): MinHash fingerprint để cross-review duplicate check

**`trust_scores`**
- `behavior_score` nullable: NULL = demo mode (chỉ content)
- `content_only` boolean: flag cho frontend biết để hiển thị caveat
- `aspects_found` (JSON): list aspect tìm được
- `breakdown` (JSON): toàn bộ signals chi tiết

**`scrape_jobs`**
- UUID primary key
- `status`: pending → processing → done | failed
- `progress`: 0–100 cho polling bar
- `restaurant_slug`: redirect target khi done

---

## 4. PhoBERT Model Loading

```python
# Singleton pattern — load 1 lần, dùng mãi
_classifier: ReviewClassifier | None = None

def get_classifier() -> ReviewClassifier:
    global _classifier
    if _classifier is None:
        _classifier = ReviewClassifier()
    return _classifier
```

**`ReviewClassifier.predict(text)`** trả về `(genuine_prob, confidence)`:
- `genuine_prob`: xác suất review là thật (0–1)
- `confidence`: max của 2 class probabilities — biểu thị model chắc chắn đến đâu

**Graceful degradation:** Nếu file `.pt` chưa có (chưa fine-tune), load base PhoBERT và log warning. Server vẫn start được.

**Batch inference:** `predict_batch(texts)` — hiệu quả hơn khi xử lý 50–100 reviews cùng lúc (padding, 1 forward pass).

---

## 5. Content Module

### Pipeline (theo thứ tự)

```
text + star_rating
    │
    ├─ [1] PhoBERT → genuine_prob × 100 = base_score
    ├─ [2] Sentiment check → penalty -25 nếu mâu thuẫn
    ├─ [3] Aspect extraction → bonus +10/+15 hoặc penalty -15
    ├─ [4] TTR (Type-Token Ratio) → penalty -10 nếu template-like
    ├─ [5] Length check → penalty -30/-20 hoặc bonus +5
    └─ [6] SimHash duplicate check → penalty -30/-40
        │
        └─ content_score = clamp(sum, 0, 100)
```

### Aspect Extraction (5 loại)

| Aspect | Cách detect |
|--------|-------------|
| Đồ ăn | Keyword set (50+ từ) + unigram/bigram matching |
| Dịch vụ | Keyword set (nhân viên, phục vụ, thái độ...) |
| Giá cả | Keyword set + regex pattern (`\d+k`, `\d+ nghìn`) |
| Không gian | Keyword set (không gian, sạch, thoáng, bàn ghế...) |
| Vị trí | Keyword set (đường, quận, gần, dễ tìm...) |

Matching dùng unigram + bigram + trigram tokens để bắt được phrases như "phục vụ tốt", "không gian đẹp".

### Vocabulary Richness (TTR)

```python
ttr = len(set(words)) / len(words)
# < 0.4 với ≥15 từ → template → -10
# ≥ 0.7 với ≥30 từ → rich → +5
```

---

## 6. Behavior Module

Tất cả signals tính từ **review card data + batch context** — không cần vào profile reviewer.

| Signal | Nguồn | Logic |
|--------|-------|-------|
| Review count | Card ("X bài đánh giá") | < 3 → -15, < 5 → -10 |
| Frequency | Timestamps trong batch | > 5/giờ cùng reviewer → -50 |
| Rating pattern | Star distribution in batch | ≥10 liên tiếp cùng sao → -15 |
| Burst detection | Daily count vs average | burst_ratio > 5x → -25 |

**Burst detection logic:**
```python
burst_ratio = target_day_count / avg_day_count
# Nếu ngày đăng review có lượng reviews >> bình thường → suspicious
```

---

## 7. Trust Engine

```
Trust Score = 0.6 × Content_Score + 0.4 × Behavior_Score
```

**Demo mode** (không có behavior data):
```
Trust Score = Content_Score
content_only = True → frontend hiển thị caveat
```

**Restaurant Risk Report** — tổng hợp cấp quán:
- `risk_level`: cao / trung_binh / thap
- Dựa trên: suspicious_ratio + new_account_ratio + cluster_count + burst_dates
- `risk_factors`: list cụ thể cho người dùng đọc

**Timeline Builder:** Đếm reviews theo ngày → trả về `[{ date, count, is_burst }]` cho Recharts.

---

## 8. Scraper (Playwright)

### Flow
```
URL → launch headless Chromium
    → navigate Google Maps
    → click tab Reviews
    → scroll panel để load lazy reviews
    → extract N review cards
    → parse: content, star, reviewer_name, reviewer_count, date
    → return ScrapedRestaurant
```

### Anti-detection
- User-Agent thực của Chrome
- Locale `vi-VN`
- Random delays giữa actions (500ms–1500ms)
- Random delays giữa cards (100ms–300ms)

### Date parsing
```python
"3 tuần trước" → datetime.now() - timedelta(weeks=3)
"2 tháng trước" → datetime.now() - timedelta(days=60)
```
Hỗ trợ cả tiếng Việt lẫn tiếng Anh (fallback).

---

## 9. API Endpoints

| Method | Path | Mô tả |
|--------|------|-------|
| POST | `/api/v1/scrape` | Tạo scrape job → 202 + job_id |
| GET | `/api/v1/scrape/status/{job_id}` | Polling: status + progress |
| GET | `/api/v1/restaurant/{slug}` | Dashboard: stats + timeline + clusters + reviews |
| POST | `/api/v1/analyze` | Demo: text + sao → content score |
| GET | `/api/v1/health` | Health check |

### Async job pattern (POST /scrape)

```
Client → POST /scrape { url }
Server → tạo ScrapeJob(status=pending) → 202 { job_id }
Server → FastAPI BackgroundTasks chạy pipeline async
Client → poll GET /scrape/status/{job_id} mỗi 3s
Server → update progress 0→100
Client → khi status=done → redirect /restaurant/{slug}
```

---

## 10. Unit Tests

**`tests/test_scoring.py`** — 20 test cases, không cần GPU/DB:

- Mock `ReviewClassifier.predict()` bằng `MagicMock`
- Test aspect extraction: food, price pattern, service, multiple aspects
- Test content module: genuine review, short review penalty, sentiment mismatch, duplicate, TTR
- Test behavior module: new account, high frequency, burst detection
- Test trust engine: badge thresholds, weighted combination, content-only mode
- Test similarity: identical texts, different texts, cluster detection

```bash
# Chạy test
cd backend
pytest tests/ -v
```

---

## 11. Chạy Backend

```bash
cd backend
pip install -r requirements.txt
playwright install chromium

# Copy .env
cp .env.example .env
# Sửa DATABASE_URL nếu cần

uvicorn backend.main:app --reload
# API docs: http://localhost:8000/docs
```
