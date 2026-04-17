# VoidRV — API Specifications

Base URL: `http://localhost:8000/api/v1`

---

## 1. POST /scrape

Nhận Google Maps URL → tạo async job → trả về ngay.

### Request
```json
{ "url": "https://www.google.com/maps/place/...", "max_reviews": 50 }
```
`max_reviews`: optional, default 50.

### Response — 202 Accepted
```json
{ "job_id": "uuid", "status": "pending", "message": "Đang khởi tạo..." }
```

---

## 2. GET /scrape/status/{job_id}

Frontend poll mỗi 3s.

### Processing
```json
{ "job_id": "uuid", "status": "processing", "progress": 65, "message": "Đang phân tích 65/100 reviews..." }
```

### Done
```json
{
  "job_id": "uuid", "status": "done", "progress": 100,
  "restaurant_slug": "banh-mi-phuong",
  "restaurant_name": "Bánh Mì Phượng",
  "reviews_scraped": 87
}
```

### Failed
```json
{ "job_id": "uuid", "status": "failed", "message": "Google Maps đang chặn scrape." }
```

---

## 3. GET /restaurant/{slug}

### Response — 200 OK
```json
{
  "restaurant": {
    "id": 1, "name": "Bánh Mì Phượng",
    "address": "2B Phan Châu Trinh, Hội An",
    "google_place_id": "ChIJ...",
    "last_scraped_at": "2026-03-15T10:00:00Z"
  },
  "stats": {
    "total_reviews": 87,
    "avg_trust_score": 66.0,
    "adjusted_rating": 3.9,
    "suspicious_ratio": 0.26,
    "new_account_ratio": 0.15,
    "badge_distribution": { "trusted": 38, "caution": 36, "suspicious": 26 },
    "risk_report": {
      "risk_level": "trung_binh",
      "risk_factors": ["26% reviews nghi ngờ", "15% ghost accounts"],
      "suspicious_ratio": 0.26,
      "new_account_ratio": 0.15,
      "cluster_count": 2,
      "burst_dates": ["2026-02-15"]
    }
  },
  "timeline": [
    { "date": "2026-01-15", "count": 3, "is_burst": false },
    { "date": "2026-02-15", "count": 47, "is_burst": true }
  ],
  "suspicious_clusters": [
    { "cluster_id": 1, "review_ids": [12, 34, 56], "avg_similarity": 0.92 }
  ],
  "reviews": [
    {
      "id": 12, "content": "Ngon lắm", "star_rating": 5,
      "reviewer_name": "Người dùng Google",
      "reviewer_review_count": 1,
      "posted_at": "2026-03-10T00:00:00Z",
      "trust_score": 22.1, "void_score": 77.9,
      "content_score": 25.0, "behavior_score": 18.0,
      "badge": "suspicious", "content_only": false,
      "aspects_found": [],
      "breakdown": { "phobert_base": 30, "length_penalty": -30, ... },
      "explanation": ["⚠ Review chỉ có 3 từ", "⚠ Ghost account"]
    }
  ]
}
```

---

## 4. POST /analyze

Demo mode — không lưu DB.

### Request
```json
{ "content": "Phở bò ngon, nước dùng đậm đà, giá 50k", "star_rating": 5 }
```

### Response — 200 OK
```json
{
  "trust_score": 76.0, "confidence": 0.88,
  "badge": "trusted", "badge_label": "Đáng tin cậy", "badge_color": "#22c55e",
  "content_only": true,
  "caveat": "Điểm này chỉ dựa trên nội dung review. Không có dữ liệu về người viết.",
  "aspects_found": ["đồ ăn", "giá cả"],
  "breakdown": {
    "phobert_base": 88, "sentiment_penalty": 0,
    "aspect_bonus": 10, "ttr_penalty": 0,
    "length_penalty": -20, "duplicate_penalty": 0,
    "content_score": 76.0, "behavior_score": null
  },
  "explanation": [
    "✓ PhoBERT: 88% xác suất là review thật",
    "✓ Đề cập 2 khía cạnh: đồ ăn, giá cả",
    "⚠ Review hơi ngắn"
  ]
}
```

---

## 5. GET /health
```json
{ "status": "ok", "model_loaded": true, "model_version": "phobert_reviewtrust_v1", "db_connected": true }
```
