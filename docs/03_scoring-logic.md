# VoidRV — Scoring Logic (2 Layers)

---

## Trust Score Formula

```
Trust Score = 0.60 × Content_Score + 0.40 × Behavior_Score
Void Score  = 100 - Trust Score

Demo mode (không có batch): Trust Score = Content Score
```

---

## Layer 1: Content Score (60%)

Pipeline chạy theo thứ tự:

```
text + star_rating
    │
    ├─ [1] PhoBERT → genuine_prob × 100 = base_score
    ├─ [2] Sentiment vs star check
    ├─ [3] Aspect extraction → bonus/penalty
    ├─ [4] TTR (vocabulary richness)
    ├─ [5] Length check
    └─ [6] SimHash duplicate vs batch
        │
        └─ content_score = clamp(sum, 0, 100)
```

### [1] PhoBERT base score
- `base_score = genuine_probability × 100`
- Confidence = max(genuine_prob, 1 - genuine_prob)

### [2] Sentiment vs Star
| Tình huống | Penalty |
|------------|---------|
| Text tích cực + star 1–2 | -25 |
| Text tiêu cực + star 4–5 | -25 |
| Khớp / trung tính | 0 |

### [3] Aspect Extraction (5 loại)
| Aspect | Detect method |
|--------|---------------|
| Đồ ăn | Keyword set + unigram/bigram |
| Dịch vụ | Keyword set (nhân viên, phục vụ...) |
| Giá cả | Keyword set + regex `\d+k` |
| Không gian | Keyword set (sạch, thoáng, đẹp...) |
| Vị trí | Keyword set (đường, quận, gần...) |

| Số aspect | Điều chỉnh |
|-----------|------------|
| ≥ 3 | +15 |
| 2 | +10 |
| 1 | 0 |
| 0 | -15 |

### [4] TTR (Type-Token Ratio)
```python
ttr = len(set(words)) / len(words)
```
| Điều kiện | Điều chỉnh |
|-----------|------------|
| TTR < 0.4 AND ≥15 từ | -10 (template-like) |
| TTR ≥ 0.7 AND ≥30 từ | +5 (rich vocabulary) |
| Khác | 0 |

### [5] Length
| Số từ | Điều chỉnh |
|-------|------------|
| < 10 | -30 |
| 10–19 | -20 |
| ≥ 50 + có aspect | +5 |
| Khác | 0 |

### [6] SimHash duplicate
| Jaccard similarity | Penalty |
|-------------------|---------|
| > 0.90 | -40 |
| 0.80–0.90 | -30 |
| < 0.80 | 0 |

---

## Layer 2: Behavior Score (40%)

Tất cả signals từ **review card data + batch context** — không cần vào profile reviewer.

```
behavior_score = clamp(100 + sum(all penalties), 0, 100)
```

### Review Count (từ card "X bài đánh giá")
| Count | Penalty |
|-------|---------|
| < 3 | -15 |
| 3–4 | -10 |
| ≥ 5 | 0 |

### Frequency (cùng reviewer trong batch)
| Điều kiện | Penalty |
|-----------|---------|
| > 5 reviews trong 1 giờ | -50 |
| > 3 reviews trong 1 giờ | -30 |

### Burst Detection
```python
burst_ratio = target_day_count / avg_daily_count
```
| burst_ratio | Penalty |
|-------------|---------|
| > 5x | -25 |
| > 3x | -15 |

### Rating Pattern
| Điều kiện | Penalty |
|-----------|---------|
| ≥ 10 reviews liên tiếp cùng sao | -15 |

---

## Badge

| Trust Score | Badge | Label | Color |
|-------------|-------|-------|-------|
| ≥ 75 | trusted | Đáng tin cậy | #22c55e |
| 50–74 | caution | Cần thận trọng | #eab308 |
| < 50 | suspicious | Nghi ngờ | #ef4444 |

---

## Restaurant-level Metrics

**Adjusted Rating:** avg(star_rating) của reviews có trust_score ≥ 50, weighted by recency.

**Risk Report:**
- `risk_level`: cao / trung_binh / thap
- Dựa vào: suspicious_ratio + new_account_ratio + cluster_count + burst_dates
- `risk_factors`: list string mô tả cụ thể

**Timeline:** `[{ date, count, is_burst }]` theo ngày → Recharts BarChart.
