# VoidRV — Kiến trúc hệ thống

---

## 1. Tổng quan kiến trúc

```
┌──────────────────────────────────────────────┐
│             React Frontend (Vite)            │
│  /  (URL input) │ /analyze │ /restaurant/:slug│
└──────────────────┬───────────────────────────┘
                   │ HTTP REST API
                   ▼
┌──────────────────────────────────────────────┐
│               FastAPI Backend                │
│                                              │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │  GG Scraper  │  │  Layer 1: Content    │  │
│  │ (Playwright) │  │  PhoBERT + rules     │  │
│  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Similarity  │  │  Layer 2: Behavior   │  │
│  │  (SimHash)   │  │  Count+Freq+Burst    │  │
│  └──────────────┘  └──────────────────────┘  │
│                    ┌──────────────────────┐  │
│                    │   Trust Engine       │  │
│                    │  60% C + 40% B       │  │
│                    └──────────────────────┘  │
└──────────────────────────────┬───────────────┘
                               │ SQLAlchemy async
                               ▼
                    ┌─────────────────┐
                    │  PostgreSQL 16  │
                    │  (reviewtrust)  │
                    └─────────────────┘
```

---

## 2. Tech Stack

| Tầng | Công nghệ |
|------|-----------|
| Frontend | React 18 + Vite 5 + TailwindCSS 3 + Recharts |
| Backend | FastAPI (Python) async |
| ML | PyTorch + HuggingFace Transformers + PhoBERT fine-tuned |
| NLP util | datasketch (SimHash/Jaccard) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x async (asyncpg) |
| Migrations | Alembic |
| Scraping | Playwright (Google Maps) |
| Deploy | Docker Compose → Railway/Render |

---

## 3. Cấu trúc Backend

```
backend/
├── main.py                  Entry point, CORS, lifespan (startup: DB init + model load)
├── routers/
│   ├── scrape.py            POST /scrape + GET /scrape/status/{id}
│   ├── analyze.py           POST /analyze (demo mode)
│   └── restaurant.py        GET /restaurant/{slug}
├── services/
│   ├── content_module.py    Layer 1: PhoBERT + sentiment + aspect + TTR + SimHash
│   ├── behavior_module.py   Layer 2: review count + frequency + burst + rating pattern
│   ├── trust_engine.py      Trust score, badge, risk report, timeline
│   ├── aspect_extractor.py  Aspect extraction (5 loại)
│   ├── similarity.py        Jaccard similarity + cluster detection
│   └── scraper.py           Google Maps scraper (Playwright)
├── ml/
│   ├── model.py             PhoBERT singleton loader + inference
│   └── weights/             phobert_voidrv.pt (git-ignored)
├── db/
│   ├── database.py          SQLAlchemy async engine + session
│   ├── models.py            ORM: Restaurant, Review, TrustScore, ScrapeJob
│   └── crud.py              DB operations
├── models/
│   └── schemas.py           Pydantic v2 request/response schemas
├── alembic/                 Migrations (Phase 2)
├── tests/
│   ├── test_scoring.py      Unit tests (no GPU/DB needed)
│   └── test_api.py          Integration tests (Phase 2)
└── requirements.txt
```

---

## 4. Data Flow

### Mode 1 — Scrape URL (flow chính)
```
POST /scrape { url }
    → tạo ScrapeJob (pending) → 202 { job_id }
    → BackgroundTask:
        → Playwright scrape Google Maps → N reviews
        → Per review:
            → Layer 1: content_module → ContentResult
            → Layer 2: behavior_module (batch) → BehaviorResult
            → trust_engine: build_trust_result → TrustResult
        → Lưu Restaurant + Reviews + TrustScores vào DB
        → ScrapeJob status = done
GET /scrape/status/{job_id}  ← polling mỗi 3s
    → status=done → redirect /restaurant/{slug}
```

### Mode 2 — Demo nhập tay
```
POST /analyze { content, star_rating }
    → content_module → ContentResult
    → build_trust_result(content, behavior=None)
    → content_only=True, Trust Score = Content Score
    → response (không lưu DB)
```

---

## 5. Database Schema

DB name: `reviewtrust`

### `restaurants`
| Column | Type | Note |
|--------|------|------|
| id | Integer PK | |
| name | String | |
| slug | String unique | URL path |
| address | Text | |
| google_place_id | String unique | dedup |
| google_maps_url | Text | |
| last_scraped_at | DateTime | cache 24h |

### `reviews`
| Column | Type | Note |
|--------|------|------|
| id | Integer PK | |
| restaurant_id | FK | |
| content | Text | |
| star_rating | SmallInt | 1–5 |
| reviewer_name | String | |
| reviewer_review_count | Integer | từ card |
| posted_relative | String | "3 tuần trước" |
| posted_at | DateTime | computed |
| simhash | BigInt | fingerprint |
| source | String | "google_maps" |

### `trust_scores`
| Column | Type | Note |
|--------|------|------|
| review_id | FK unique | |
| content_score | Float | |
| behavior_score | Float nullable | NULL = demo mode |
| trust_score | Float | 0–100 |
| void_score | Float | 100 - trust_score |
| badge | String | trusted/caution/suspicious |
| content_only | Boolean | |
| aspects_found | JSON | list |
| breakdown | JSON | signals chi tiết |
| explanation | JSON | list string |

### `scrape_jobs`
| Column | Type | Note |
|--------|------|------|
| id | UUID PK | |
| restaurant_id | FK nullable | |
| status | String | pending→processing→done/failed |
| progress | Integer | 0–100 |
| message | Text | |
| restaurant_slug | String | redirect target |
| error_message | Text | |

---

## 6. Scoring Logic

```
Trust Score = 0.60 × Content_Score + 0.40 × Behavior_Score
Void Score  = 100 - Trust Score

Badge:
  ≥ 75  → "Đáng tin cậy" / trusted   (#22c55e)
  50–74 → "Cần thận trọng" / caution  (#eab308)
  < 50  → "Nghi ngờ" / suspicious     (#ef4444)

Demo mode (no batch): Trust Score = Content Score, content_only = True
```

---

## 7. API Endpoints

| Method | Path | Mô tả |
|--------|------|-------|
| POST | `/api/v1/scrape` | Scrape URL → 202 + job_id |
| GET | `/api/v1/scrape/status/{job_id}` | Polling job |
| GET | `/api/v1/restaurant/{slug}` | Dashboard data |
| POST | `/api/v1/analyze` | Demo: content score only |
| GET | `/api/v1/health` | Model + DB status |
