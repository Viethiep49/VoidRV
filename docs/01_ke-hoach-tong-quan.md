# VoidRV — Kế hoạch tổng quan

> **Dự án:** Hệ thống xác định độ tin cậy review nhà hàng — giúp traveler biết nên tin review nào
> **Sinh viên:** Trương Viết Hiệp
> **Trường:** HUTECH — Khoa CNTT, HTTTUD
> **Loại:** Đồ án chuyên ngành

---

## 1. Bài toán

Khi traveler đọc review nhà hàng trên Google Maps, họ không biết:
- **Nội dung** có thật không? (spam, generic, copy-paste, sentiment mâu thuẫn)
- **Người viết** có đáng tin không? (ghost account, farm worker, bot)
- **Rating** có bị đẩy lên không? (review farm, burst campaign)

**VoidRV** nhận URL Google Maps → scrape reviews + đối chiếu Foody.vn → phân tích 3 layer → trả về:
- **Void Score:** mức độ "rỗng" (giả) của reviews
- **Adjusted Rating:** rating thật sau khi loại review nghi ngờ
- **Top Trusted Reviews:** những review đáng đọc nhất
- **Reviewer Archetypes:** ai viết review này (Foodie thật? Ghost? Farm?)

---

## 2. Hướng giải quyết — 3 Layers

| Layer | Tên | Câu hỏi | Phương pháp | Nguồn dữ liệu |
|-------|-----|---------|-------------|---------------|
| 1 | Content | Nội dung thật không? | PhoBERT + aspect + TTR + SimHash | Text + sao |
| 2 | Identity | Người viết đáng tin? | Stylometry + credibility signals | Text + card data + batch |
| 3 | Context | Bối cảnh bình thường? | Burst + distribution + cross-platform | Batch + Foody.vn |

**Trust Score = 40% Content + 30% Identity + 30% Context**
**Void Score = 100 - Trust Score**

---

## 3. Hình thức sản phẩm

**Web Application** gồm 3 trang:

### Trang chủ `/`
- Input: paste Google Maps URL
- Trigger scrape → polling → redirect dashboard

### Trang `/restaurant/:slug` — Dashboard (flow chính)

| Component | Mô tả |
|-----------|-------|
| Void Score Meter | Gauge hiển thị Void Score + Trust Score |
| Adjusted Rating | Rating thật vs Google Maps rating |
| Cross-Platform | So sánh GG vs Foody (rating, volume) |
| Archetype Breakdown | Pie chart: Foodie/Casual/Newbie/Ghost/Farm |
| Top Trusted Reviews | 5–10 review đáng đọc nhất (sorted by identity + content) |
| Risk Report | Cảnh báo cụ thể: burst dates, clusters, new account ratio |
| Timeline Chart | Reviews theo thời gian, highlight burst days |
| Suspicious Clusters | Nhóm reviews copy-paste + style giống nhau |
| Review List | Từng review + badge + 3 scores + archetype |

### Trang `/analyze` — Demo nhập tay
- Text + số sao → Content Score + partial Identity Score
- Caveat: "thiếu data reviewer và cross-platform"

---

## 4. Phạm vi (Scope)

### Làm

**Core:**
- Web app: URL scrape → 3-layer analysis → traveler dashboard
- Google Maps scraper (Playwright)
- Foody.vn scraper (httpx + BeautifulSoup4) — cross-platform
- Fine-tune PhoBERT cho fake/genuine classification

**Layer 1 — Content:**
- PhoBERT base score + confidence
- Sentiment vs star check
- Aspect extraction: food/service/price/ambiance/location
- TTR + Length penalty
- SimHash copy-paste detection + cluster grouping

**Layer 2 — Identity:**
- Review count scoring (từ card)
- Writing effort (length × aspect × TTR)
- Specificity detection (tên món, giá, nhân viên)
- Experience markers (regex: "lần thứ 3", "hôm qua")
- Emotion authenticity (mixed emotions = thật)
- Stylometry (TF-IDF char n-grams + cosine similarity → cluster farm)
- Vietnamese spam patterns ("ngon lắm" + "sẽ quay lại" combo)
- Reviewer Archetypes (5 loại)

**Layer 3 — Context:**
- Burst detection (timeline spike)
- Rating pattern (batch)
- Rating distribution forensics (chi-square test)
- Cross-platform gap (Google Maps vs Foody rating/sentiment/volume)
- Trust decay (recency weighting)

**Output:**
- Void Score + Trust Score
- Adjusted Rating (loại review nghi ngờ, weighted by recency)
- Top Trusted Reviews
- Restaurant Risk Report
- Reviewer Archetype distribution

**ML/Academic:**
- Ablation study (1-layer vs 2-layer vs 3-layer)
- Cross-platform analysis notebook

### KHÔNG làm
- Không vào profile reviewer (chỉ dùng card data + text)
- Không browser extension / mobile app
- Không xử lý ảnh / GPS / ViT
- Không eKYC / blockchain / DID
- Không Redis / Celery / Vector DB

---

## 5. Timeline dự kiến

| Tuần | Công việc |
|------|-----------|
| 1 | Tải datasets, explore, setup môi trường, init GitHub |
| 2 | Scrape Google Maps + Foody ~20-30 quán, label, generate GPT fake |
| 3 | Merge dataset → fine-tune PhoBERT → metrics |
| 4 | Ablation study notebook (1L vs 2L vs 3L) |
| 5 | Backend: DB schema + GG scraper + Foody scraper + async job |
| 6 | Backend: Content + Identity + Context modules + Trust Engine + API |
| 7 | Frontend: Dashboard (Void Score, Adjusted Rating, Archetypes, Timeline) |
| 8 | Frontend: Analyze demo + Top Trusted Reviews + Polish UI |
| 9 | Tích hợp end-to-end, test 5+ quán, fix bugs |
| 10 | Deploy Docker → Railway/Render, viết báo cáo, slide demo |
