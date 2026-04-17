# VoidRV — Data Pipeline (ML)

> **Status:** Phase 4 — defer. Train khi app frontend hoàn thiện.

---

## Tổng quan

```
Step 1: Dataset có sẵn (HuggingFace)
    → ViSpamReviews (UIT 2024) — label sẵn

Step 2: Scrape bổ sung
    → Google Maps ~20–30 quán → label heuristic + thủ công

Step 3: Generate fake
    → GPT-4o tạo fake reviews tiếng Việt nhà hàng

Step 4: Tổng hợp & Fine-tune
    → Merge → clean → split → fine-tune PhoBERT
    → Target: ~3000–5000 samples, F1 ≥ 0.83

Step 5: Export
    → backend/ml/weights/phobert_voidrv.pt
```

---

## Dataset

### Dataset A — ViSpamReviews *(ưu tiên)*

| Thông tin | Chi tiết |
|-----------|---------|
| Link | `huggingface.co/datasets/visolex/ViSpamReviews` |
| Tác giả | UIT (VNU-HCM) |
| Paper | arXiv:2405.13292 (2024) |
| Label | 0 = non-spam, 1 = spam |
| License | CC BY-NC-SA 4.0 |

### Dataset B — Scrape tự
- Google Maps: ~20–30 quán nhà hàng
- Label: heuristic (burst accounts, ghost accounts) + thủ công
- Script: `data/scripts/label_reviews.py`

### Dataset C — GPT-generated fake
- Prompt GPT-4o: fake restaurant reviews tiếng Việt (template-heavy, generic)
- ~500–1000 samples

---

## Fine-tune

```python
# Model base
model = AutoModelForSequenceClassification.from_pretrained(
    "vinai/phobert-base", num_labels=2
)

# Hyperparams
epochs = 3–5
batch_size = 16
lr = 2e-5
max_length = 256

# Target
F1 ≥ 0.83 trên val set
```

Notebook: `notebooks/01_finetune_phobert.ipynb`

---

## Ablation Study

So sánh 3 cấu hình:
1. Content-only (Trust = Content)
2. Content + Behavior (Trust = 0.60C + 0.40B) — **current**

Notebook: `notebooks/02_ablation_study.ipynb`

---

## Graceful Degradation

Backend hiện tại: nếu `weights/phobert_voidrv.pt` chưa có → load base PhoBERT + log warning. Server vẫn start được, score sẽ kém chính xác hơn.
