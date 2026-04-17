# VoidRV — Kế hoạch tổng quan

> **Dự án:** Hệ thống xác định độ tin cậy review nhà hàng
> **Sinh viên:** Trương Viết Hiệp — HUTECH, CNTT, HTTTUD

---

## 1. Bài toán

Traveler đọc review nhà hàng trên Google Maps không biết:
- **Nội dung** có thật không? (spam, generic, copy-paste, sentiment mâu thuẫn)
- **Người viết** có đáng tin không? (ghost account, farm worker)
- **Rating** có bị đẩy lên không? (burst campaign, new account flood)

**VoidRV** nhận URL Google Maps → scrape reviews → phân tích 2 layer → trả về:
- **Trust Score / Void Score** — mức độ tin cậy tổng thể
- **Adjusted Rating** — rating thật sau khi lọc review nghi ngờ
- **Risk Report** — cảnh báo cụ thể: burst days, suspicious clusters
- **Top Trusted Reviews** — những review đáng đọc nhất

---

## 2. Hướng giải quyết — 2 Layers

| Layer | Tên | Câu hỏi | Phương pháp |
|-------|-----|---------|-------------|
| 1 | Content (60%) | Nội dung thật không? | PhoBERT + sentiment + aspect + TTR + SimHash |
| 2 | Behavior (40%) | Reviewer đáng tin không? | Review count + frequency + burst + rating pattern |

```
Trust Score = 0.60 × Content + 0.40 × Behavior
Void Score  = 100 - Trust Score
```

---

## 3. Hình thức sản phẩm

**Web Application** gồm 3 trang:

### `/` — Trang chủ
- Input: paste Google Maps URL → polling → redirect dashboard

### `/restaurant/:slug` — Dashboard
| Component | Mô tả |
|-----------|-------|
| Trust Score Gauge | Vòng cung Trust Score + Void Score |
| Adjusted Rating | Rating thật vs Google Maps rating |
| Risk Report | risk_level + risk_factors |
| Timeline Chart | Reviews theo ngày, burst day highlight |
| Suspicious Clusters | Nhóm reviews copy-paste |
| Review List | Từng review + badge + breakdown |

### `/analyze` — Demo nhập tay
- Text + số sao → Content Score only
- Caveat: "không có reviewer data"

---

## 4. Phạm vi (Scope)

### Làm
- Google Maps scraper (Playwright)
- Layer 1 Content: PhoBERT + sentiment + aspect + TTR + SimHash
- Layer 2 Behavior: review count + frequency + burst + rating pattern
- Fine-tune PhoBERT (binary: genuine/fake)
- Web app 3 trang

### Chưa làm / defer
- Foody.vn cross-platform (defer)
- Ablation study notebook (Phase 4)
- ML fine-tune (Phase 4 — train riêng)

### KHÔNG làm
- Browser extension, mobile app, GPS/ViT, eKYC, blockchain, Redis/Celery/Vector DB

---

## 5. Timeline (phases)

| Phase | Công việc | Trạng thái |
|-------|-----------|------------|
| P1 | Docs update + Plan | ✅ Xong |
| P2 | Backend hardening (Alembic, tests) | 🔄 |
| P3 | Frontend (scaffold → 3 trang) | 🔄 |
| P4 | ML pipeline (fine-tune, ablation) | ⏸ Defer |
| P5 | Integration + Deploy | 🔄 |

Chi tiết: `docs/plan.md`
