# VoidRV — API Specifications

Base URL: `http://localhost:8000/api/v1`

---

## 1. POST /scrape — Scrape reviews từ Google Maps + Foody

Entry point chính. Nhận URL → tạo job → trả về ngay (async).

### Request

```json
{
  "url": "https://www.google.com/maps/place/...",
  "max_reviews": 100
}
```

| Field | Type | Required | Note |
|-------|------|----------|------|
| url | string | Yes | Google Maps URL |
| max_reviews | int | No | Default 100, max 200 |

### Response — 202 Accepted

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Đang khởi tạo scrape job..."
}
```

---

## 2. GET /scrape/status/{job_id} — Polling trạng thái

Frontend poll mỗi 3 giây.

### Response — Processing

```json
{
  "job_id": "...",
  "status": "processing",
  "progress": 65,
  "message": "Đang phân tích 65/100 reviews..."
}
```

### Response — Done

```json
{
  "job_id": "...",
  "status": "done",
  "progress": 100,
  "restaurant_slug": "banh-mi-phuong",
  "restaurant_name": "Bánh Mì Phượng",
  "reviews_scraped": 87,
  "foody_found": true
}
```

### Response — Failed

```json
{
  "job_id": "...",
  "status": "failed",
  "message": "Google Maps đang chặn scrape. Thử lại sau."
}
```

---

## 3. GET /restaurant/{slug} — Dashboard quán

### Response — 200 OK

```json
{
  "restaurant": {
    "id": 1,
    "name": "Bánh Mì Phượng",
    "address": "2B Phan Châu Trinh, Hội An",
    "google_place_id": "ChIJ...",
    "google_rating": 4.8,
    "foody_url": "https://www.foody.vn/...",
    "foody_rating": 3.9,
    "foody_review_count": 89,
    "last_scraped_at": "2026-03-15T10:00:00Z"
  },
  "summary": {
    "total_reviews": 87,
    "void_score_avg": 34,
    "trust_score_avg": 66,
    "adjusted_rating": 3.9,
    "google_rating": 4.8,
    "cross_platform_gap": 0.9,
    "distribution": {
      "trusted": 38.0,
      "caution": 36.0,
      "suspicious": 26.0
    },
    "archetype_distribution": {
      "foodie": 23,
      "casual": 41,
      "newbie": 14,
      "ghost": 15,
      "farm": 7
    }
  },
  "risk_report": {
    "risk_level": "trung_binh",
    "risk_factors": [
      "26% reviews bị đánh dấu 'Nghi ngờ'",
      "15% ghost accounts",
      "Chênh lệch GG vs Foody: 0.9 sao"
    ],
    "traveler_summary": "Quán khá, nhưng ~1/4 reviews không đáng tin. Rating thật khoảng 3.9 sao."
  },
  "top_trusted_reviews": [
    {
      "id": 45,
      "content": "Phở tái gầu nước trong, hành tươi. Chờ 15 phút vì đông. Giá 65k hợp lý.",
      "star_rating": 4,
      "reviewer_name": "Nguyễn Văn A",
      "reviewer_review_count": 142,
      "reviewer_archetype": "foodie",
      "trust_score": 89,
      "identity_score": 91,
      "content_score": 88
    }
  ],
  "timeline": [
    { "date": "2026-01-15", "count": 3, "is_burst": false },
    { "date": "2026-02-15", "count": 47, "is_burst": true }
  ],
  "suspicious_clusters": [
    {
      "cluster_id": 1,
      "review_ids": [12, 34, 56],
      "type": "copy_paste",
      "avg_similarity": 0.92
    }
  ],
  "reviews": [
    {
      "id": 12,
      "content": "Ngon lắm",
      "star_rating": 5,
      "reviewer_name": "Người dùng Google",
      "reviewer_review_count": 1,
      "reviewer_archetype": "ghost",
      "posted_at": "2026-03-10T00:00:00Z",
      "trust_score": 22.1,
      "void_score": 77.9,
      "content_score": 25.0,
      "identity_score": 18.0,
      "context_score": 30.0,
      "badge": "suspicious",
      "explanation": [
        "⚠ PhoBERT: 28% xác suất là review thật",
        "⚠ Review chỉ có 3 từ",
        "⚠ Ghost account (1 bài đánh giá)",
        "⚠ Không đề cập chi tiết cụ thể",
        "⚠ Thuộc nhóm copy-paste 3 reviews"
      ]
    }
  ]
}
```

---

## 4. POST /analyze — Demo nhập tay

Không lưu DB. Tính Content + partial Identity.

### Request

```json
{
  "content": "Bánh mì ngon, nhân thịt heo quay giòn, giá 25k, ăn ở tầng 2 thoáng mát",
  "star_rating": 5
}
```

### Response — 200 OK

```json
{
  "trust_score": 76.0,
  "void_score": 24.0,
  "badge": "trusted",
  "badge_label": "Đáng tin cậy",
  "badge_color": "#22c55e",
  "content_only": false,
  "partial_identity": true,
  "caveat": "Điểm Identity chỉ dựa trên nội dung text. Không có data reviewer và cross-platform.",
  "breakdown": {
    "content_score": 79.0,
    "identity_score": 72.0,
    "context_score": null,
    "content_details": {
      "phobert_genuine_prob": 0.88,
      "confidence": 0.91,
      "sentiment": "positive",
      "sentiment_penalty": 0,
      "aspects_found": ["đồ ăn", "giá cả", "không gian"],
      "aspect_bonus": 15,
      "ttr": 0.72,
      "ttr_penalty": 5,
      "word_count": 18,
      "length_penalty": -20,
      "max_similarity": 0.0,
      "duplicate_penalty": 0
    },
    "identity_details": {
      "review_count": null,
      "writing_effort": 6,
      "specificity_found": ["tên món", "giá tiền", "vị trí"],
      "specificity_bonus": 15,
      "experience_markers": ["ngồi tầng 2"],
      "experience_bonus": 5,
      "emotion_ratio": 0.0,
      "emotion_bonus": 0,
      "stylometry_penalty": 0,
      "vn_spam_penalty": 0,
      "reviewer_archetype": null
    }
  },
  "explanation": [
    "✓ PhoBERT: 88% xác suất là review thật (độ chắc chắn 91%)",
    "✓ Sentiment tích cực khớp với 5 sao",
    "✓ Đề cập 3 khía cạnh: đồ ăn, giá cả, không gian",
    "✓ Đề cập tên món cụ thể (bánh mì, thịt heo quay), giá (25k)",
    "✓ Có dấu hiệu trải nghiệm thực (ngồi tầng 2)",
    "⚠ Review hơi ngắn (18 từ)",
    "ℹ Không có data reviewer — Identity Score chỉ tính partial"
  ]
}
```

---

## 5. GET /health — Health check

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "phobert_voidrv_v1",
  "db_connected": true
}
```
