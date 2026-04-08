# VoidRV — Data Pipeline

---

## 1. Tổng quan

```
Phase 1: Dataset có sẵn (ưu tiên đầu tiên)
    → Tải từ HuggingFace — label sẵn

Phase 2: Scrape bổ sung (domain nhà hàng)
    → Google Maps + Foody.vn → label heuristic + thủ công

Phase 3: Generate fake (bổ sung)
    → GPT-4o tạo fake reviews tiếng Việt nhà hàng

Phase 4: Tổng hợp & Fine-tune
    → Merge → clean → split → fine-tune PhoBERT

Phase 5: Tích hợp
    → Model .pt load trong FastAPI
```

---

## 2. Phase 1 — Dataset có sẵn

### Dataset A — ViSpamReviews *(quan trọng nhất)*

| Thông tin | Chi tiết |
|-----------|---------|
| Link | `huggingface.co/datasets/visolex/ViSpamReviews` |
| Tác giả | UIT (ĐH Công nghệ Thông tin VNU-HCM) |
| Paper | arXiv:2405.13292 (2024) |
| Label | Binary: `0 = non-spam`, `1 = spam` |
| License | CC BY-NC-SA 4.0 |

### Dataset B — ViSpamDetection v2

| Thông tin | Chi tiết |
|-----------|---------|
| Link | `huggingface.co/datasets/clapAI/ViSpamDetectionv2` |
| Số samples | **19,870 rows** |
| Label | Spam / non-spam |

### Dataset C — vi-ntc-scv

| Thông tin | Chi tiết |
|-----------|---------|
| Link | `huggingface.co/datasets/thainq107/vi-ntc-scv` |
| Số samples | **50,000 rows** |
| Domain | Review đồ ăn, dịch vụ |
| Label | Sentiment 0/1 → convert positive dài → genuine |

### Dataset D — sonlam1102/vispamdetection

| Thông tin | Chi tiết |
|-----------|---------|
| Link | `huggingface.co/datasets/sonlam1102/vispamdetection` |
| Paper | arXiv:2207.14636 (2022) |
| Note | Cần agree terms trên HuggingFace |

### Dataset E — AiGen-FoodReview *(tham khảo)*

| Thông tin | Chi tiết |
|-----------|---------|
| Link | `huggingface.co/datasets/davanstrien/AiGen-FoodReview` |
| Note | Tiếng Anh — chỉ tham khảo methodology generate fake |

---

## 3. Phase 2 — Scrape bổ sung

### Google Maps

**Tool:** Playwright + playwright-stealth
**Target:** 20–30 quán TP.HCM + Hà Nội, ~50–100 reviews/quán → ~1,000–2,000 reviews
**Output:** `data/raw/gmaps_reviews.jsonl`

### Foody.vn

**Tool:** httpx + BeautifulSoup4
**Target:** Cùng 20–30 quán trên → scrape Foody reviews
**Output:** `data/raw/foody_reviews.jsonl`
**Mục đích:** Cross-platform matching data + bổ sung genuine reviews

### Label heuristic

```python
def heuristic_label(review) -> int | None:
    text = review['content']
    words = len(text.split())
    rc = review['reviewer_review_count']

    if words < 5 and rc <= 2:
        return 1  # fake
    if words >= 30 and rc >= 10:
        return 0  # genuine
    return None  # label thủ công
```

Label thủ công ~200–300 samples uncertain.

---

## 4. Phase 3 — Generate fake (GPT-4o)

**Target:** ~300–400 fake reviews

| Pattern | Số lượng |
|---------|----------|
| Generic ngắn ("Ngon lắm", "Tuyệt vời") | 80 |
| Khen cường điệu | 80 |
| Copy-paste biến thể | 80 |
| Sentiment mâu thuẫn | 60 |
| Spam quảng cáo | 50 |

---

## 5. Tổng hợp dataset cuối

| Nguồn | Ước tính | Label |
|-------|----------|-------|
| ViSpamReviews + ViSpamDetection v2 | ~5,000 chọn lọc | 0/1 sẵn |
| vi-ntc-scv (convert) | ~1,000 | genuine |
| Google Maps scrape | ~800 | heuristic + thủ công |
| Foody scrape | ~500 | genuine (higher baseline) |
| GPT-generated fake | ~300–400 | fake |
| **Tổng** | **~3,000–5,000** | balanced |

```
Split: 80% train / 10% val / 10% test
```

---

## 6. Fine-tune PhoBERT

### Config

| Param | Value |
|-------|-------|
| Base model | `vinai/phobert-base` |
| Epochs | 3–5 |
| Batch size | 16 |
| Learning rate | 2e-5 |
| Max length | 256 tokens |
| GPU | RTX 3060 12GB (~4-6 GB VRAM) |

### Target metrics

| Metric | Target |
|--------|--------|
| Accuracy | ≥ 85% |
| F1 macro | ≥ 0.83 |
| Precision | ≥ 0.80 |
| Recall | ≥ 0.80 |

**Output:** `backend/ml/weights/phobert_voidrv.pt`

---

## 7. Ablation Study *(bắt buộc)*

File: `notebooks/ablation_study.ipynb`

| Cấu hình | Accuracy | F1 |
|----------|----------|-----|
| Content only (Layer 1) | ? | ? |
| Content + Identity (L1+L2) | ? | ? |
| Content + Context (L1+L3) | ? | ? |
| **Full 3-layer (L1+L2+L3)** | ? | ? |
| Baseline: rule-based only | ? | ? |

**Mục đích:** Chứng minh mỗi layer đóng góp. Khi thầy hỏi "Identity layer có giúp ích không?" — có số liệu.

---

## 8. Tài liệu tham khảo data

| Paper | Năm | Link |
|-------|-----|------|
| "Detecting Spam Reviews on Vietnamese E-commerce Websites" (UIT) | 2022 | arXiv:2207.14636 |
| "Metadata Integration for Spam Reviews Detection..." (UIT) | 2024 | arXiv:2405.13292 |
| "AiGen-FoodReview: A Multimodal Dataset..." | 2024 | arXiv:2401.08825 |
