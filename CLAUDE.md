# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Dự án: VoidRV (ReviewTrust)

**Mô tả:** Hệ thống xác định độ tin cậy review nhà hàng tại Việt Nam.
**Loại:** Đồ án chuyên ngành — HTTTUD, năm 3, HUTECH — Trương Viết Hiệp.

---

## Kiến trúc tổng thể

```
voidrv/
├── backend/           FastAPI — REST API, ML inference, 2-layer scoring engine
│   ├── routers/       analyze.py | restaurant.py | scrape.py
│   ├── services/      content_module, behavior_module, trust_engine, scraper, similarity, aspect_extractor
│   ├── ml/            PhoBERT load & inference (singleton, loaded on startup)
│   ├── db/            SQLAlchemy async ORM (asyncpg) + CRUD
│   └── models/        Pydantic schemas (schemas.py)
├── frontend/          React + Vite + TailwindCSS (scaffold pending — no package.json yet)
│   └── src/           pages/ | components/ | api/
├── data/              Dataset scripts
├── notebooks/         PhoBERT fine-tune notebook
└── docs/              Tài liệu đồ án
```

**Data flow — 2 mode:**

```
[Mode 1] User paste Google Maps URL
    → POST /api/v1/scrape → 202 { job_id }
    → Playwright scrape: reviews × (text, star, reviewer card)
    → Per review: Content Module → Behavior Module → Trust Engine
    → GET /api/v1/scrape/status/{job_id} polling
    → Redirect → /restaurant/:slug

[Mode 2 — Demo] User nhập text + số sao
    → POST /api/v1/analyze → Content Module only (no batch = no behavior)
    → { trust_score, badge, breakdown, content_only: true }
```

---

## Commands

**Backend:**
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
uvicorn backend.main:app --reload    # from project root
# hoặc:
cd backend && uvicorn main:app --reload

pytest backend/tests/ -v             # run from project root
pytest backend/tests/test_scoring.py::TestContentModule -v   # single class
```

**Frontend (khi đã có package.json):**
```bash
cd frontend && npm install && npm run dev
```

**Docker:**
```bash
docker-compose up --build
# Backend: http://localhost:8000  |  Frontend: http://localhost:3000
```

---

## Backend — Services

| File | Vai trò |
|------|---------|
| `content_module.py` | PhoBERT inference + sentiment check + aspect + TTR + length + SimHash duplicate |
| `behavior_module.py` | Reviewer card data: review count penalty + frequency + burst + rating pattern |
| `trust_engine.py` | Gộp 2 layer → trust score, badge, void score, explanation |
| `similarity.py` | Jaccard similarity + cluster detection (datasketch) |
| `aspect_extractor.py` | Rule-based: đồ ăn / dịch vụ / giá cả / không gian / vị trí |
| `scraper.py` | Google Maps scraper (Playwright) |

> **Không có:** `foody_scraper.py`, `context_module.py`, `identity_module.py` — chưa implement.

---

## Scoring Logic — 2 Layers

### Layer 1: Content Score (60%)
- **Base:** PhoBERT genuine_prob × 100
- **Sentiment check:** text vs star mâu thuẫn → -25
- **Aspect:** ≥3 → +15; 2 → +10; 0 → -15
- **TTR:** < 0.4 → -10; > 0.7 (long text) → +5
- **Length:** < 10 từ → -30; 10–19 → -20; ≥50 + aspect → +5
- **SimHash duplicate:** > 90% → -40; 80–90% → -30

### Layer 2: Behavior Score (40%)
- **Review count:** < 3 → -15; < 5 → -10
- **Frequency:** > 6 reviews trong 1 giờ (cùng reviewer) → penalty nặng
- **Burst:** ≥ 15 tài khoản mới cùng ngày → burst penalty
- **Rating pattern:** liên tiếp cùng sao → -15

### Trust Score & Void Score
```
Trust Score = 0.60 × Content + 0.40 × Behavior
              (content only mode nếu không có batch: Trust = Content)
Void Score  = 100 - Trust Score

Badge:
  ≥ 75  → "Đáng tin cậy" / "trusted"   (#22c55e)
  50–74 → "Cần thận trọng" / "caution"  (#eab308)
  < 50  → "Nghi ngờ" / "suspicious"     (#ef4444)
```

---

## API Endpoints

| Method | Path | Mô tả |
|--------|------|-------|
| POST | `/api/v1/analyze` | Demo: 1 review → content score only, không lưu DB |
| GET | `/api/v1/restaurant/{slug}` | Dashboard quán |
| POST | `/api/v1/scrape` | Scrape Google Maps URL → 202 + job_id |
| GET | `/api/v1/scrape/status/{job_id}` | Polling job |
| GET | `/api/v1/health` | Model + DB status |

---

## Database Schema

DB name: `reviewtrust` (xem `backend/.env.example`)

| Bảng | Columns chính |
|------|--------------|
| `restaurants` | id, name, slug (unique), google_place_id, google_maps_url, last_scraped_at |
| `reviews` | id, restaurant_id, content, star_rating, reviewer_name, reviewer_review_count, posted_at, simhash, source |
| `trust_scores` | id, review_id (unique), content_score, behavior_score, trust_score, void_score, badge, explanation (JSON) |
| `scrape_jobs` | id, restaurant_id, status, error_message |

Migrations: Alembic (`alembic upgrade head`) — migrations folder chưa tạo.

---

## ML Model

- **Model:** `vinai/phobert-base` fine-tuned binary (genuine vs fake)
- **Singleton:** `get_classifier()` trong `ml/model.py` — load on startup, cache suốt session
- **Weights:** `backend/ml/weights/phobert_voidrv.pt` (git-ignored)
- **Training:** `notebooks/` — ~3–5k samples, RTX 3060 12GB

---

## Environment Variables

```bash
# backend/.env (copy từ .env.example)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reviewtrust
```

```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Scope — KHÔNG làm

Redis, Celery, Vector DB, browser extension, mobile app, eKYC, blockchain, GPS/ViT.
