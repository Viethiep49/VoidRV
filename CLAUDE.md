# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Dự án: VoidRV

**Mô tả:** Hệ thống xác định độ tin cậy review nhà hàng tại Việt Nam — giúp traveler biết nên tin review nào.  
**Loại:** Đồ án chuyên ngành — Hệ thống thông tin ứng dụng, năm 3.  
**Trường:** Đại học Công nghệ TP.HCM (HUTECH) — Khoa CNTT.  
**Sinh viên:** Trương Viết Hiệp — làm một mình, không có teammate.

**Ý nghĩa tên:** "Void" = khoảng trống, sự giả rỗng ẩn sau review. "RV" = Review. VoidRV chiếu sáng vào khoảng trống giữa review và thực tế.

---

## Kiến trúc tổng thể

```
voidrv/
├── backend/           FastAPI — REST API, ML inference, 3-layer scoring engine
│   ├── routers/       API endpoints
│   ├── services/      Business logic (content, identity, context, trust engine)
│   ├── ml/            PhoBERT model loading & inference
│   ├── db/            SQLAlchemy ORM + CRUD
│   └── models/        Pydantic schemas
├── frontend/          React + Vite + TailwindCSS — web app
│   └── src/
│       ├── pages/     Home, Analyze, Restaurant
│       └── components/ ScoreGauge, VoidMeter, Breakdown, ReviewList, ...
├── data/              Dataset: raw scrape, labeled, scripts
├── notebooks/         Fine-tune PhoBERT notebook + ablation study
├── docs/              Tài liệu đồ án + proposal
└── docker-compose.yml
```

**Data flow — 2 mode:**

```
[Mode 1 — Main] User paste Google Maps URL
    → POST /api/v1/scrape → 202 Accepted { job_id }
    → Playwright scrape: N reviews × (text, star, reviewer card data)
    → Auto-search Foody.vn (httpx + BS4) → cross-platform data
    → Với mỗi review:
        → Layer 1 — Content:  PhoBERT + rules
        → Layer 2 — Identity: stylometry + credibility signals
        → Layer 3 — Context:  batch patterns + cross-platform
        → TrustEngine: 40%C + 30%I + 30%X → lưu DB
    → Tổng hợp: Adjusted Rating + Void Score + Archetypes + Top Trusted Reviews
    → GET /api/v1/scrape/status/{job_id} → polling
    → Redirect → /restaurant/:slug dashboard

[Mode 2 — Demo] User nhập tay text + số sao
    → POST /api/v1/analyze
    → Layer 1 — Content: full
    → Layer 2 — Identity: partial (writing effort + specificity + experience markers)
    → Layer 3 — Context: N/A
    → Trust Score = weighted content + partial identity
    → Response: { trust_score, void_score, badge, breakdown, content_only: true }
```

---

## Tech Stack

| Tầng | Công nghệ |
|------|-----------|
| Frontend | React 18 + Vite 5 + TailwindCSS 3 + Recharts |
| Backend | FastAPI (Python) |
| ML | PyTorch + HuggingFace Transformers + PhoBERT (vinai/phobert-base) fine-tuned |
| NLP util | datasketch (SimHash), scikit-learn (TF-IDF stylometry) |
| Database | PostgreSQL 16 (JSONB cho metadata) |
| ORM | SQLAlchemy 2.x |
| Scraping | Playwright (Google Maps), httpx + BeautifulSoup4 (Foody.vn) |
| Deploy | Docker Compose → Railway/Render |

**KHÔNG dùng:** Redis, Celery, Vector DB, TorchServe, MongoDB, browser extension.

---

## Backend (FastAPI / Python)

**Cấu trúc:**
```
backend/
├── main.py                  Entry point, app init, model loading on startup
├── routers/
│   ├── analyze.py           POST /api/v1/analyze — demo mode
│   ├── restaurant.py        GET /api/v1/restaurant/{slug} — dashboard
│   └── scrape.py            POST /api/v1/scrape — scrape Google Maps + Foody
├── services/
│   ├── content_module.py    PhoBERT inference + sentiment + aspect + TTR + SimHash
│   ├── identity_module.py   Stylometry + credibility + experience markers + archetypes
│   ├── context_module.py    Burst + rating distribution + cross-platform gap
│   ├── trust_engine.py      Gộp 3 layer, tính badge, Void Score, Adjusted Rating
│   ├── similarity.py        SimHash copy-paste detection (datasketch)
│   ├── aspect_extractor.py  Aspect extraction (5 loại)
│   ├── scraper.py           Google Maps scraper (Playwright)
│   └── foody_scraper.py     Foody.vn scraper (httpx + BS4)
├── ml/
│   ├── model.py             Load PhoBERT fine-tuned, inference function (~50ms/review trên GPU)
│   └── weights/             .pt file (git-ignored)
├── db/
│   ├── database.py          SQLAlchemy async setup
│   ├── models.py            ORM: Restaurant, Review, TrustScore
│   └── crud.py              DB operations
├── models/
│   └── schemas.py           Pydantic request/response schemas
├── requirements.txt
└── Dockerfile
```

**Chạy dev:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API docs: http://localhost:8000/docs
```

**Chạy test:**
```bash
pytest tests/ -v
pytest tests/test_trust_engine.py -v
```

---

## Frontend (React + Vite + TailwindCSS)

**Các trang chính:**
- `/` — Trang chủ: paste URL → trigger scrape
- `/analyze` — Demo: nhập tay review → Content + partial Identity score
- `/restaurant/:slug` — Dashboard: Void Score, Adjusted Rating, Archetypes, Top Trusted Reviews, Timeline

**Chạy dev:**
```bash
cd frontend
npm install
npm run dev
```

---

## Database Schema (PostgreSQL)

| Bảng | Columns chính |
|------|--------------|
| `restaurants` | id, name, address, google_place_id, foody_url, foody_rating, foody_review_count, created_at |
| `reviews` | id, restaurant_id, content, star_rating, reviewer_metadata (JSONB), source ('google_maps'/'foody'), style_vector, created_at |
| `trust_scores` | id, review_id, content_score, identity_score, context_score, trust_score, void_score, badge, reviewer_archetype, explanation (JSONB), model_version, created_at |

---

## Scoring Logic — 3 Layers

### Layer 1: Content Score (40%)
- **Base:** PhoBERT fine-tuned genuine probability × 100
- **Sentiment check:** text vs star mâu thuẫn → -25
- **Aspect extraction:** food/service/price/ambiance/location — ≥3 → +15; 2 → +10; 0 → -15
- **TTR:** < 0.4 → -10; > 0.7 long → +5
- **Length:** < 10 từ → -30; 10–19 → -20; ≥50 + aspect → +5
- **SimHash:** > 90% → -40; 80–90% → -30

### Layer 2: Identity Score (30%)
- **Review count:** < 3 → -15; 3–4 → -10; ≥ 20 → +15
- **Writing effort:** word_count × aspect_count × TTR
- **Specificity:** tên món cụ thể, giá tiền, nhân viên → +5 mỗi loại
- **Experience markers:** "lần thứ 3", "hôm qua", "đi với gia đình" → +5 mỗi cái
- **Emotion authenticity:** có cả khen + chê → +10 (mixed emotions = thật)
- **Stylometry:** TF-IDF char 3-grams → cosine similarity vs batch → cluster farm → -20
- **Vietnamese spam patterns:** "ngon lắm" + "sẽ quay lại" combo, emoji spam → -15

### Layer 3: Context Score (30%)
- **Burst detection:** spike > 5x avg → -25; new accounts cùng ngày → -20
- **Rating pattern:** ≥10 liên tiếp cùng sao → -15; >80% 5★ → -10
- **Rating distribution forensics:** chi-square test vs natural J-curve → -15 nếu bất thường
- **Cross-platform (Foody):** rating gap > 1★ → -25; gap < 0.5★ → +15; đồng thuận → +20
- **Trust decay:** review > 1 năm → weight 0.5

### Trust Score & Void Score
```
Trust Score = 0.40 × Content + 0.30 × Identity + 0.30 × Context
Void Score  = 100 - Trust Score

Badge:
  ≥ 75  → "Đáng tin cậy"  (xanh #22c55e)
  50–74 → "Cần thận trọng" (vàng #eab308)
  < 50  → "Nghi ngờ"       (đỏ #ef4444)

Adjusted Rating = avg(star) of reviews where Trust ≥ 50, weighted by recency
```

### Reviewer Archetypes
| Type | Điều kiện |
|------|-----------|
| Foodie thật | review_count ≥ 20 + text dài + nhiều aspect + style unique |
| Casual reviewer | review_count 5–19 + text trung bình |
| Newbie | review_count < 5 + text ngắn nhưng không template |
| Ghost account | review_count ≤ 2 + text generic + không aspect |
| Farm suspect | style trùng cluster + timing trùng burst |

---

## ML Pipeline

- **Model:** vinai/phobert-base fine-tuned cho binary classification (genuine vs fake)
- **Dataset:** ~3,000–5,000 samples (HuggingFace datasets + scrape + GPT-generated)
- **Training:** 3–5 epochs, batch 16, lr 2e-5, RTX 3060 12GB, ~30 phút
- **Inference:** load model on startup, ~50ms/review trên GPU
- **Weights:** `backend/ml/weights/phobert_voidrv.pt` (git-ignored)

---

## API Endpoints

| Method | Path | Mô tả |
|--------|------|-------|
| POST | `/api/v1/analyze` | Demo: phân tích 1 review (text + sao) → content + partial identity |
| GET | `/api/v1/restaurant/{slug}` | Dashboard quán: Void Score, Adjusted Rating, Archetypes, Top Reviews |
| POST | `/api/v1/scrape` | Scrape Google Maps URL + auto Foody → 202 + job_id |
| GET | `/api/v1/scrape/status/{job_id}` | Polling trạng thái scrape job |
| GET | `/api/v1/health` | Health check + model status |

---

## Environment Variables

```
# backend/.env
DATABASE_URL=postgresql://user:pass@localhost:5432/voidrv

# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Scope rõ ràng — KHÔNG làm

- Không browser extension
- Không GPS / xử lý ảnh / ViT
- Không mobile app
- Không eKYC / xác thực danh tính thật
- Không blockchain / DID
- Không Redis / Celery / Vector DB

---

## Tài liệu

Chi tiết xem trong `docs/`:
- `00_proposal.md` — Proposal đầy đủ: bài toán, 3-layer approach, 6 phase
- `01_ke-hoach-tong-quan.md` — Kế hoạch, timeline, scope
- `02_kien-truc-he-thong.md` — Kiến trúc, tech stack, DB schema, luồng xử lý
- `03_scoring-logic.md` — Chi tiết 3-layer scoring rules
- `04_data-pipeline.md` — Thu thập, label, fine-tune PhoBERT
- `05_api-specs.md` — API request/response chi tiết
- `06_tai-lieu-tham-khao.md` — Papers, datasets, thư viện

---

## Deploy

```bash
docker-compose up --build
# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
```

Production: Railway hoặc Render (free tier).
