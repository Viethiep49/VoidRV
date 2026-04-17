# VoidRV — Master Plan

> Chi tiết từng task: `docs/superpowers/plans/2026-04-18-voidrv-full-plan.md`

## Hiện trạng (2026-04-18)

| Phần | Trạng thái |
|------|------------|
| Backend core (services, routers, DB models) | ✅ Xong |
| Unit tests | ✅ Xong |
| Báo cáo backend | ✅ docs/bao-cao/01_backend.md |
| Docs (6 files) | ✅ Đã sync (Phase 1) |
| Alembic migrations | ✅ Xong |
| Integration tests | ✅ Xong |
| Frontend | ❌ Phase 3 |
| ML fine-tune | ⏸ Phase 4 (defer) |
| Deploy | ❌ Phase 5 |

---

## Phase 1 — Docs & Plan `[ ]`

- [ ] Cập nhật docs/01 → 05 cho đúng 2-layer thực tế
- [ ] Tạo plan.md (file này)
- [ ] Commit

---

## Phase 2 — Backend Hardening `[✅ DONE]`

- [x] Alembic migrations (4 bảng)
- [x] Integration tests (test_api.py) — 9 tests
- [x] URL validation cho ScrapeRequest
- [x] Báo cáo: docs/bao-cao/02_backend-hardening.md

---

## Phase 3 — Frontend `[ ]`

- [ ] Scaffold: Vite + React + TailwindCSS
- [ ] Components: ScoreGauge, Badge, ScoreBreakdown, ReviewList, TimelineChart, RiskReport
- [ ] Pages: `/` (scrape URL) · `/analyze` (demo) · `/restaurant/:slug` (dashboard)
- [ ] Báo cáo: docs/bao-cao/03_frontend.md

---

## Phase 4 — ML Pipeline `[⏸ DEFER]`

- [ ] Dataset prep + labeling (~3000–5000 samples)
- [ ] Fine-tune PhoBERT (F1 ≥ 0.83)
- [ ] Ablation study notebook
- [ ] Báo cáo: docs/bao-cao/04_ml-pipeline.md

---

## Phase 5 — Integration & Deploy `[ ]`

- [ ] E2E test (3–5 quán thật)
- [ ] Docker Compose
- [ ] Deploy Railway/Render
- [ ] Báo cáo: docs/bao-cao/05_integration-deploy.md

---

## Scoring hiện tại (2-layer)

```
Trust Score = 0.60 × Content + 0.40 × Behavior
Void Score  = 100 - Trust Score
Badge: ≥75 trusted · 50-74 caution · <50 suspicious
```
