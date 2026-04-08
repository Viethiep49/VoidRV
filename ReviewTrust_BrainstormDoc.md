# ReviewTrust — Tài liệu brainstorm dự án

> Ý tưởng gốc từ thầy: "Đi chơi ở Đà Nẵng ghé Bánh Mì Phượng — làm sao biết quán đó có review tốt, hay xác thực được người review?"

---

## 1. Bài toán

Khi người dùng đọc review trên Google Maps, TripAdvisor, Foody... họ đối mặt với 2 lớp vấn đề:

```
Tôi đọc review Bánh Mì Phượng trên Google Maps
        ↓
Review này có thật không?  ←── Lớp 1: Xác thực NỘI DUNG review
Người viết có thật không?  ←── Lớp 2: Xác thực DANH TÍNH reviewer
```

Các nền tảng hiện tại (Google Maps, TripAdvisor, Foody) không giải quyết được bài toán này triệt để. Review farm, tài khoản ảo, nội dung spam vẫn tồn tại tràn lan.

---

## 2. Định hướng giải pháp — ReviewTrust Framework

Thay vì build một app review mới cạnh tranh với Google Maps, hướng đề xuất là xây dựng **infrastructure layer** — một framework/module có thể gắn vào bất kỳ nền tảng review nào đã có sẵn.

Tương tự như:
- **Stripe** = "Payment as a Service" — ai cũng có thể dùng
- **Disqus** = "Comment as a Service"
- **ReviewTrust** = "Trust as a Service"

### Lợi thế của hướng này

- Giải quyết vấn đề **cold start**: không cần user mới, tận dụng hàng triệu review sẵn có
- Một lần build, nhiều platform dùng chung
- Không cạnh tranh với Google Maps — bổ sung giá trị cho nó
- Có tính ứng dụng thực tế cao, phù hợp với nghiên cứu ứng dụng

---

## 3. Ba lớp xác thực (Core Engine)

Hệ thống gồm 3 module verify chạy song song, độc lập, output gộp vào Trust Score Engine.

### Lớp 1 — Proof of Visit (Chứng minh đã đến thật)

**Bài toán:** Ảnh người dùng chụp có thực sự chụp tại quán đó không?

**Công nghệ chính:**
- **Vision Transformer (ViT-B/16 hoặc ViT-L/16)** pretrained trên ImageNet, fine-tune với dataset ảnh quán ăn Việt Nam
- Hoặc **CLIP** (Contrastive Language-Image Pretraining, OpenAI) — so sánh ảnh với text mô tả quán

**Pipeline kỹ thuật:**
1. Quán đăng ký hệ thống → upload ảnh "ground truth" (biển hiệu, nội thất, menu)
2. User chụp ảnh tại quán → gửi lên kèm GPS + timestamp EXIF
3. ViT tính **cosine similarity** giữa ảnh user và embedding của quán trong vector database
4. GPS verify: tọa độ phải trong bán kính 100m của quán
5. Timestamp EXIF phải khớp giờ hoạt động

**Chống gian lận ảnh:**
- EXIF metadata check (ảnh screenshot không có EXIF camera thật)
- Image forensics: detect ảnh chỉnh sửa bằng **ELA (Error Level Analysis)**
- Liveness check tuỳ chọn: selfie với quán ở background

**Data cần:**
- Ảnh ground truth: scrape từ Google Maps, Foody, Facebook page của quán
- GPS coordinates 50.000+ quán ăn VN: Google Places API hoặc OpenStreetMap
- Giờ hoạt động: Google Places API field `opening_hours`

**Vector database:** Pinecone hoặc Weaviate — similarity search < 50ms

> ⚡ Đây là phần trực tiếp liên quan đến luận văn Vision Transformer — hướng **place recognition**, ít nghiên cứu tại VN.

---

### Lớp 2 — Verified Identity (Người dùng có thật)

**Bài toán:** Người này có thật không? Có phải farm tài khoản không?

**Hướng eKYC (thực tế nhất tại VN):**
- Tích hợp **VNeID API** (Bộ Công An VN, mở từ 2023) — xác thực CCCD chip
- Mỗi CCCD chỉ liên kết 1 tài khoản reviewer → không thể tạo nhiều account
- Dữ liệu nhận về: họ tên, ngày sinh, ảnh CCCD (không lưu, chỉ verify)

**Hướng DID — Decentralized Identity (hướng nghiên cứu):**
- Chuẩn **W3C DID + Verifiable Credentials**
- User tự giữ credential trên điện thoại, không server nào lưu danh tính
- Dùng **zero-knowledge proof** để chứng minh "tôi là người thật" mà không tiết lộ danh tính cụ thể
- Library: `did-jwt`, `veramo` (Node.js)

**Behavioral Fingerprint (phát hiện bot):**
- Keystroke dynamics, scroll pattern, session behavior
- Device fingerprint: User-Agent, screen size, timezone
- Model: **Random Forest** hoặc **Isolation Forest** để detect anomaly

---

### Lớp 3 — Credibility Score (Review đáng tin không)

**Bài toán:** Nội dung review có đáng tin không, có phải spam không?

**NLP Pipeline:**
- Model: **PhoBERT** (BERT tiếng Việt, VinAI) — tốt nhất cho text tiếng Việt
- Fine-tune PhoBERT cho task: genuine review vs fake review
- Features NLP:
  - Độ cụ thể: đề cập tên món, giá, nhân viên → score cao
  - Sentiment consistency: nội dung phải khớp số sao
  - Copy-paste detection: MinHash so sánh với toàn bộ DB
  - Named Entity Recognition: trích xuất địa điểm, thời gian, sản phẩm

**Cross-source Verification:**
- Thu thập từ nhiều nguồn: Google Maps API, Foody (scraping), Facebook Graph API
- Tính correlation: review xấu đồng loạt nhiều nơi cùng lúc → flag suspicious
- **Graph Neural Network**: 10 account cùng review 1 quán trong 1 giờ → review farm

**Reviewer History Score:**
- Account age: tài khoản tạo hôm nay review ngay → penalty
- Review diversity: chỉ review 1 quán duy nhất → suspicious
- Geographic consistency: reviewer Hà Nội review quán Đà Nẵng 5 ngày liên tiếp → flag

**Data:**
- PhoBERT pretrained: HuggingFace `vinai/phobert-base` (miễn phí)
- Google Maps API: Places API, $200 credit/tháng
- Dataset fake review: Yelp Chi et al. 2012 (benchmark chuẩn), adapt sang tiếng Việt

---

## 4. Trust Score Engine

**Input:** Output từ 3 lớp — mỗi lớp cho score 0–100

**Công thức:**
```
Trust Score = 0.40 × Proof_of_Visit
            + 0.35 × Identity_Score
            + 0.25 × Credibility_Score
```

Trọng số có thể học qua supervised learning nếu có labeled data.

**Ngưỡng badge:**

| Score | Badge | Hiển thị |
|---|---|---|
| ≥ 80 | Đã xác thực đầy đủ (xanh) | Hiện mặc định |
| 50–79 | Xác thực một phần (vàng) | Hiện mặc định |
| < 50 | Chưa xác thực (xám) | Ẩn mặc định, bấm mới hiện |

---

## 5. Kiến trúc tích hợp — 3 mode

### Mode A — Browser Extension (không cần platform hợp tác)

Nhanh nhất để làm proof of concept. Extension detect URL pattern → scrape DOM → gọi API → inject badge.

- Công nghệ: Chrome Extension Manifest V3, TypeScript, `MutationObserver` cho SPA
- Hoạt động ngay trên Google Maps, TripAdvisor mà không cần xin phép platform

### Mode B — JS Widget Embed (platform chủ động tích hợp)

Platform chỉ cần dán 2 dòng:

```html
<script src="https://reviewtrust.vn/widget.js"></script>
<div data-reviewtrust="banh-mi-phuong-hoian"></div>
```

- Load async, không chặn render
- Giao tiếp qua `postMessage` để bypass CORS
- Giống cách Disqus hoặc Facebook Comment Box hoạt động

### Mode C — REST API (tích hợp sâu, enterprise)

```http
POST /api/v1/verify-review
Content-Type: application/json

{
  "reviewer_id": "...",
  "photo_url": "...",
  "gps": { "lat": 15.88, "lng": 108.33 },
  "content": "Bánh mì ngon, giá 20k..."
}
```

Response:
```json
{
  "trust_score": 87,
  "badge": "verified",
  "breakdown": {
    "proof_of_visit": 92,
    "identity": 85,
    "credibility": 80
  }
}
```

Phù hợp với Foody, Agoda — platform có engineering team muốn tự kiểm soát UI.

---

## 6. Tech Stack tổng thể

| Tầng | Công nghệ |
|---|---|
| Mobile SDK | React Native + Expo (camera, GPS, EXIF) |
| Backend API | FastAPI (Python) |
| ML serving | TorchServe hoặc Triton Inference Server |
| Vector DB | Pinecone (cloud) hoặc Qdrant (self-host) |
| Database | PostgreSQL + Redis (cache trust score) |
| Queue | Celery + Redis (async ML inference) |
| eKYC | VNeID API hoặc VNPT eKYC SDK |
| NLP | PhoBERT via HuggingFace Transformers |
| Vision | ViT hoặc CLIP via PyTorch |

---

## 7. Điểm novelty để bảo vệ với thầy

### Novelty kỹ thuật

1. **ViT cho place recognition** — không phải object detection hay face recognition thông thường. Đây là hướng còn ít nghiên cứu tại Việt Nam, dữ liệu bản địa (ảnh quán ăn VN) tạo ra đóng góp riêng biệt.

2. **Privacy-preserving identity** — dùng zero-knowledge proof / DID thay vì lưu danh tính tập trung. Align với xu hướng toàn cầu về self-sovereign identity.

3. **Multi-modal trust scoring** — kết hợp vision + NLP + behavioral signal. Không phụ thuộc vào bất kỳ 1 modality đơn lẻ nào, robust hơn các hệ thống chỉ dùng NLP.

4. **Framework hướng tích hợp** — giải quyết vấn đề cold start của các app review độc lập. Đây là đóng góp về system design, không chỉ ML.

### Scope đề xuất cho luận văn

| Phần | Nội dung | Mức độ |
|---|---|---|
| Core (luận văn chính) | Lớp 1: ViT scene match + GPS verify | Deep |
| Extension | Lớp 3: PhoBERT NLP credibility | Medium |
| Future work | Lớp 2: DID + eKYC identity | Đề cập, không implement |
| Demo | Browser extension inject badge vào Google Maps | Proof of concept |

---

## 8. Tóm tắt một trang (cho buổi trình thầy)

> **Bài toán:** Review fake và tài khoản ảo làm mất niềm tin của người dùng vào các nền tảng review hiện tại.
>
> **Giải pháp:** ReviewTrust — một framework xác thực review 3 lớp (chứng minh đã đến thật, danh tính người dùng, nội dung đáng tin) có thể gắn vào bất kỳ nền tảng review nào qua browser extension, JS widget, hoặc REST API.
>
> **Novelty:** Ứng dụng Vision Transformer cho bài toán place recognition tại Việt Nam, kết hợp multi-modal signal (ảnh + GPS + NLP) để tạo trust score không thể giả mạo.
>
> **Hướng nghiên cứu:** Fine-tune ViT/CLIP trên dataset ảnh quán ăn Việt Nam, đánh giá độ chính xác place recognition so với baseline GPS-only, tích hợp thành proof-of-concept browser extension demo trên Google Maps.

---

*Tài liệu được tổng hợp từ buổi brainstorm — ReviewTrust Identity Verification System*
