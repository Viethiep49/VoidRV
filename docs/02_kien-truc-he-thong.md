# VoidRV — Kiến trúc hệ thống

---

## 1. Tổng quan kiến trúc

```
┌──────────────────────────────────────────────┐
│             React Frontend                   │
│  Home (URL input) │ /restaurant/:slug        │
│                   │ /analyze (demo)          │
└──────────────────┬───────────────────────────┘
                   │ HTTP (REST API)
                   ▼
┌──────────────────────────────────────────────┐
│               FastAPI Backend                │
│                                              │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │  GG Scraper  │  │  Layer 1: Content    │  │
│  │ (Playwright) │  │  PhoBERT + rules     │  │
│  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Foody Scraper│  │  Layer 2: Identity   │  │
│  │ (httpx+BS4)  │  │  Stylometry+signals  │  │
│  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Similarity  │  │  Layer 3: Context    │  │
│  │  (SimHash)   │  │  Burst+CrossPlatform │  │
│  └──────────────┘  └──────────────────────┘  │
│                    ┌──────────────────────┐  │
│                    │    Trust Engine      │  │
│                    │  40C + 30I + 30X     │  │
│                    └──────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│             PostgreSQL 16                    │
│  restaurants │ reviews │ trust_scores        │
└──────────────────────────────────────────────┘
```

---

## 2. Cấu trúc thư mục

```
voidrv/
├── backend/
│   ├── main.py                     Entry point, model loading on startup
│   ├── routers/
│   │   ├── analyze.py              POST /api/v1/analyze — demo mode
│   │   ├── restaurant.py           GET  /api/v1/restaurant/{slug}
│   │   └── scrape.py               POST /api/v1/scrape + GET /status/{job_id}
│   ├── services/
│   │   ├── content_module.py       Layer 1: PhoBERT + sentiment + aspect + TTR + SimHash
│   │   ├── identity_module.py      Layer 2: stylometry + credibility + experience + archetypes
│   │   ├── context_module.py       Layer 3: burst + distribution + cross-platform + decay
│   │   ├── trust_engine.py         Gộp 3 layer → Trust/Void Score, Adjusted Rating, Top Reviews
│   │   ├── aspect_extractor.py     Aspect extraction (food/service/price/ambiance/location)
│   │   ├── similarity.py           SimHash + cluster detection
│   │   ├── scraper.py              Google Maps scraper (Playwright)
│   │   └── foody_scraper.py        Foody.vn scraper (httpx + BS4)
│   ├── ml/
│   │   ├── model.py                Load PhoBERT fine-tuned, inference
│   │   └── weights/                .pt file (git-ignored)
│   ├── db/
│   │   ├── database.py             SQLAlchemy async setup
│   │   ├── models.py               ORM: Restaurant, Review, TrustScore, ScrapeJob
│   │   └── crud.py                 DB operations
│   ├── models/
│   │   └── schemas.py              Pydantic request/response schemas
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx            URL input + loading
│   │   │   ├── Restaurant.tsx      Dashboard traveler
│   │   │   └── Analyze.tsx         Demo nhập tay
│   │   ├── components/
│   │   │   ├── VoidMeter.tsx       Void Score gauge
│   │   │   ├── AdjustedRating.tsx  Google Maps vs VoidRV rating
│   │   │   ├── CrossPlatform.tsx   GG vs Foody comparison
│   │   │   ├── ArchetypeChart.tsx  Pie chart reviewer archetypes
│   │   │   ├── TopTrustedReviews.tsx  Top N reviews đáng đọc
│   │   │   ├── ScoreGauge.tsx      Trust score per review
│   │   │   ├── Breakdown.tsx       3-layer score breakdown
│   │   │   ├── ReviewList.tsx      Danh sách reviews
│   │   │   ├── TimelineChart.tsx   Recharts timeline + burst highlight
│   │   │   ├── SuspiciousCluster.tsx Nhóm copy-paste + style
│   │   │   ├── RiskReport.tsx      Restaurant risk summary
│   │   │   ├── RatingDistribution.tsx Rating bar chart + anomaly flag
│   │   │   └── ScrapeProgress.tsx  Loading state
│   │   ├── api/
│   │   │   └── client.ts           Axios + API calls + polling
│   │   └── App.tsx                 Router
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── data/
│   ├── raw/                        Reviews scrape (jsonl)
│   ├── labeled/                    Reviews labeled (jsonl)
│   └── scripts/
│       ├── scrape_gmaps.py         Scrape data cho training
│       ├── scrape_foody.py         Scrape Foody data
│       ├── generate_fake.py        Generate fake reviews (GPT)
│       └── label_tool.py           CLI label tool
├── notebooks/
│   ├── finetune_phobert.ipynb      Fine-tune notebook
│   └── ablation_study.ipynb        1L vs 2L vs 3L comparison
├── docker-compose.yml
├── .gitignore
├── docs/
└── CLAUDE.md
```

---

## 3. Tech Stack

| Tầng | Công nghệ | Version | Lý do |
|------|-----------|---------|-------|
| Frontend | React + Vite | React 18, Vite 5 | SPA nhanh, HMR |
| UI | TailwindCSS | 3.x | Utility-first |
| Charts | Recharts | 2.x | Timeline, pie chart, bar chart |
| Backend | FastAPI | 0.110+ | Async, auto Swagger |
| ML | PyTorch + Transformers | torch 2.x | PhoBERT inference |
| NLP Model | PhoBERT (vinai/phobert-base) | - | BERT tốt nhất tiếng Việt |
| Stylometry | scikit-learn | 1.x | TF-IDF + cosine similarity |
| Copy-paste | datasketch (SimHash) | - | Duplicate detection |
| Scraper GG | Playwright + playwright-stealth | - | Headless browser |
| Scraper Foody | httpx + BeautifulSoup4 | - | Nhẹ, không cần JS render |
| Database | PostgreSQL | 16 | JSONB, production-ready |
| ORM | SQLAlchemy | 2.x | Async support |
| Deploy | Docker Compose | - | 1 command |
| Hosting | Railway / Render | Free tier | Demo |

### Không dùng

| Công nghệ | Lý do |
|------------|-------|
| Redis | Traffic thấp |
| Celery | Job tracking bằng DB đủ |
| Vector DB | Không cần semantic similarity |
| TorchServe | Overkill, load model thẳng |
| MongoDB | PostgreSQL JSONB đủ |

---

## 4. Database Schema

### Bảng `restaurants`

| Column | Type | Note |
|--------|------|------|
| id | SERIAL PK | |
| name | VARCHAR(255) | Tên quán |
| address | TEXT | Địa chỉ |
| google_place_id | VARCHAR(100) UNIQUE | ID từ Google Maps |
| google_maps_url | TEXT | URL gốc |
| foody_url | TEXT | URL Foody.vn (nullable) |
| foody_rating | FLOAT | Rating trên Foody (nullable) |
| foody_review_count | INT | Số review trên Foody (nullable) |
| last_scraped_at | TIMESTAMP | Cache |
| created_at | TIMESTAMP | |

### Bảng `reviews`

| Column | Type | Note |
|--------|------|------|
| id | SERIAL PK | |
| restaurant_id | FK → restaurants.id | |
| content | TEXT | Nội dung review |
| star_rating | SMALLINT | 1–5 |
| reviewer_name | VARCHAR(255) | Tên hiển thị |
| reviewer_review_count | INT | Số review trên card |
| reviewer_metadata | JSONB | posted_relative, posted_at, extra |
| simhash | BIGINT | SimHash content |
| style_vector | TEXT | TF-IDF fingerprint (nullable) |
| source | VARCHAR(50) | 'google_maps' / 'foody' |
| created_at | TIMESTAMP | |

### Bảng `trust_scores`

| Column | Type | Note |
|--------|------|------|
| id | SERIAL PK | |
| review_id | FK → reviews.id UNIQUE | |
| content_score | FLOAT | Layer 1 (0–100) |
| identity_score | FLOAT | Layer 2 (0–100, nullable) |
| context_score | FLOAT | Layer 3 (0–100, nullable) |
| trust_score | FLOAT | Weighted final (0–100) |
| void_score | FLOAT | 100 - trust_score |
| badge | VARCHAR(20) | trusted/caution/suspicious |
| reviewer_archetype | VARCHAR(20) | foodie/casual/newbie/ghost/farm |
| explanation | JSONB | Array lý do |
| model_version | VARCHAR(50) | |
| created_at | TIMESTAMP | |

### Bảng `scrape_jobs`

| Column | Type | Note |
|--------|------|------|
| id | UUID PK | job_id |
| url | TEXT | Google Maps URL |
| status | VARCHAR(20) | pending/processing/done/failed |
| progress | INT | 0–100% |
| restaurant_id | FK nullable | Sau khi scrape xong |
| error_message | TEXT | nullable |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

---

## 5. Luồng xử lý

### Mode 1 — Scrape từ URL (flow chính)

```
[1] Client POST /api/v1/scrape { url: "https://maps.google.com/..." }
    → Tạo ScrapeJob → return 202 { job_id }

[2] Background: Scrape Google Maps (Playwright)
    → Extract restaurant name + address + N review cards
    → Lưu reviews vào DB (source='google_maps')

[3] Background: Auto-search Foody.vn
    → httpx GET foody.vn/search?q={name}+{quận}
    → Parse kết quả → tìm quán match
    → Scrape Foody rating + review count + M reviews
    → Lưu foody_url, foody_rating, foody_review_count vào restaurants
    → Lưu Foody reviews vào DB (source='foody')

[4] Analyze pipeline (mỗi Google Maps review):
    Layer 1: Content
        → PhoBERT → genuine_prob → base_score
        → Sentiment check, aspect extraction, TTR, length, SimHash
        → content_score

    Layer 2: Identity
        → Review count scoring
        → Writing effort, specificity, experience markers
        → Emotion authenticity
        → Stylometry: TF-IDF char 3-grams → cosine vs batch → farm cluster
        → Vietnamese spam patterns
        → identity_score + reviewer_archetype

    Layer 3: Context
        → Burst detection (timeline)
        → Rating pattern (batch)
        → Rating distribution forensics (chi-square)
        → Cross-platform gap (GG rating vs Foody rating)
        → Trust decay (recency weight)
        → context_score

    Trust Engine:
        → trust_score = 0.4×C + 0.3×I + 0.3×X
        → void_score = 100 - trust_score
        → badge + explanation
        → Lưu trust_scores

[5] Tổng hợp cấp quán:
    → Adjusted Rating = avg(star) of trusted reviews × recency
    → Top Trusted Reviews = top 5–10 by (identity + content)
    → Archetype distribution = pie chart data
    → Risk Report + Timeline + Clusters

[6] Client polling → done → redirect /restaurant/:slug
```

### Mode 2 — Nhập tay (demo)

```
[1] POST /api/v1/analyze { content, star_rating }
[2] Layer 1: Content → full
[3] Layer 2: Identity → partial (writing effort, specificity, experience only)
[4] Layer 3: Context → N/A
[5] Trust = content + partial identity (ghi caveat)
[6] Return response (không lưu DB)
```
