# VoidRV — Proposal Đồ Án Chuyên Ngành

> **Sinh viên:** Trương Viết Hiệp
> **MSSV:** *(điền vào)*
> **Trường:** Đại học Công nghệ TP.HCM (HUTECH)
> **Khoa:** Công nghệ Thông tin — Hệ thống Thông tin Ứng dụng
> **Năm học:** 2025–2026
> **GVHD:** *(điền vào)*

---

## 1. Tên đề tài

**VoidRV: Hệ thống xác định độ tin cậy review nhà hàng sử dụng phân tích nội dung (PhoBERT), nhận diện danh tính reviewer (Stylometry), và đối chiếu đa nền tảng (Google Maps × Foody)**

---

## 2. Đặt vấn đề

### 2.1 Thực trạng

Review nhà hàng trên Google Maps là yếu tố quyết định hành vi người tiêu dùng tại Việt Nam, đặc biệt khi đi du lịch. Tuy nhiên, hệ sinh thái review tồn tại vấn đề nghiêm trọng:

- **Review farm:** Dịch vụ "tăng sao" rao bán công khai — hàng trăm review 5 sao giá vài trăm nghìn đồng
- **Ghost account:** Tài khoản chỉ có 1–2 review, tạo ra để farm rồi bỏ
- **Copy-paste:** Cùng đoạn text đăng lại trên nhiều tài khoản với thay đổi nhỏ
- **Sentiment mâu thuẫn:** Nội dung tiêu cực nhưng cho 5 sao (hoặc ngược lại)
- **Rating inflation:** Quán mới 3 tháng đã có 500+ reviews 5 sao — bất thường

Traveler không có công cụ nào để trả lời: **"Quán này thật sự tốt, hay rating bị đẩy lên?"**

### 2.2 Khoảng trống

Các nghiên cứu phát hiện fake review tiếng Việt (UIT 2022, 2024) tập trung vào **e-commerce** (Tiki, Shopee). Chưa có hệ thống nào:
- Xây dựng cho domain **nhà hàng** tại Việt Nam
- Kết hợp **3 layer**: nội dung (NLP) + danh tính reviewer (stylometry) + bối cảnh đa nền tảng
- Cung cấp **Adjusted Rating** (rating thật sau khi loại review giả) cho người dùng cuối
- **Đối chiếu cross-platform** (Google Maps vs Foody.vn) để verify
- Phân loại reviewer thành **archetypes** (Foodie thật, Ghost account, Farm suspect)

### 2.3 Câu hỏi nghiên cứu

1. PhoBERT fine-tuned có thể phân loại fake/genuine review nhà hàng tiếng Việt với F1 ≥ 0.83 không?
2. Thêm Identity Layer (stylometry + credibility signals) có cải thiện đáng kể so với chỉ dùng content?
3. Cross-platform comparison (Google Maps vs Foody) có phải là tín hiệu hiệu quả để phát hiện rating inflation?
4. Các reviewer archetype nào phổ biến nhất trong các chiến dịch review farm tại Việt Nam?

---

## 3. Mục tiêu

### Mục tiêu chính
Xây dựng web application giúp traveler xác định quán ăn nào đáng tin: phân tích toàn bộ reviews từ Google Maps URL, đối chiếu với Foody.vn, đánh giá từng review qua 3 layer, và đưa ra **Adjusted Rating + Top Trusted Reviews**.

### Mục tiêu cụ thể
1. Fine-tune PhoBERT đạt F1 ≥ 0.83 cho binary classification (genuine/fake)
2. Xây dựng Identity Scoring dựa trên stylometry (TF-IDF) + credibility signals — không cần vào profile
3. Tích hợp cross-platform comparison Google Maps × Foody.vn
4. Phân loại reviewer thành 5 archetypes (Foodie, Casual, Newbie, Ghost, Farm suspect)
5. Tính Adjusted Rating (loại review nghi ngờ) + Void Score (mức độ "rỗng" của review)
6. Xây dựng web app hoàn chỉnh: scrape → analyze → traveler dashboard
7. Triển khai lên Railway/Render

---

## 4. Hướng tiếp cận

### 4.1 Kiến trúc 3 Layer

```
Google Maps URL
        │
        ▼
┌─── Scrape Google Maps (Playwright) ───┐
│   N reviews × (text, star, card data) │
└───────────────┬───────────────────────┘
                │
        ┌───────▼──────────────────────┐
        │ Auto-search Foody.vn (httpx) │
        │ → foody_rating, foody_count  │
        │ → M reviews (text, star)     │
        └───────────────┬──────────────┘
                        │
    ┌───────────────────▼───────────────────┐
    │     VoidRV Trust Engine (3 Layer)     │
    │                                       │
    │  Layer 1: Content (40%)               │
    │    PhoBERT genuine_prob               │
    │    + Sentiment vs star                │
    │    + Aspect extraction (5 loại)       │
    │    + TTR + Length + SimHash            │
    │                                       │
    │  Layer 2: Identity (30%)              │
    │    Review count + Writing effort      │
    │    + Specificity (tên món, giá, NV)   │
    │    + Experience markers (regex)       │
    │    + Emotion authenticity             │
    │    + Stylometry (TF-IDF char n-gram)  │
    │    + Vietnamese spam patterns         │
    │    → Reviewer Archetype               │
    │                                       │
    │  Layer 3: Context (30%)               │
    │    Burst detection (timeline)         │
    │    + Rating pattern (batch)           │
    │    + Rating distribution forensics    │
    │    + Cross-platform gap (GG vs Foody) │
    │    + Trust decay (recency)            │
    │                                       │
    │  Trust = 0.4C + 0.3I + 0.3X          │
    │  Void Score = 100 - Trust             │
    │  Adjusted Rating                      │
    │  Top Trusted Reviews                  │
    └───────────────────────────────────────┘
```

### 4.2 Điểm khác biệt so với nghiên cứu liên quan

| Tiêu chí | UIT 2022/2024 | VoidRV |
|----------|---------------|--------|
| Domain | E-commerce (Tiki/Shopee) | **Nhà hàng** (Google Maps + Foody) |
| Layers | 1–2 (content + metadata) | **3 layers** (content + identity + context) |
| Identity | Cần metadata profile đầy đủ | **Stylometry + card data** (không cần profile) |
| Cross-platform | Không | **Google Maps × Foody.vn** |
| Reviewer classification | Không | **5 archetypes** |
| Output | Spam/non-spam label | **Adjusted Rating + Void Score + Top Reviews** |
| Use case | Research | **Traveler-oriented web app** |
| Timeline/Burst | Không | Có |
| Cluster detection | Không | SimHash grouping + style clustering |

---

## 5. Dữ liệu

### 5.1 Nguồn dataset có sẵn

| Dataset | Tác giả | Size | Label | Link |
|---------|---------|------|-------|------|
| ViSpamReviews | UIT (arXiv:2405.13292, 2024) | ~N* | spam/non-spam | `huggingface.co/datasets/visolex/ViSpamReviews` |
| ViSpamDetection v2 | clapAI | 19,870 | spam/non-spam | `huggingface.co/datasets/clapAI/ViSpamDetectionv2` |
| vi-ntc-scv | thainq107 | 50,000 | sentiment 0/1 | `huggingface.co/datasets/thainq107/vi-ntc-scv` |

### 5.2 Thu thập bổ sung

- Scrape Google Maps ~1,000–2,000 reviews nhà hàng (Playwright) → label heuristic + thủ công
- Scrape Foody.vn tương ứng → cross-platform matching
- Generate ~300–400 fake reviews tiếng Việt domain nhà hàng bằng GPT-4o

### 5.3 Dataset huấn luyện cuối

```
Target: ~3,000–5,000 samples (balanced genuine/fake)
Split: 80% train / 10% val / 10% test
```

---

## 6. Tech Stack

| Tầng | Công nghệ |
|------|-----------|
| Frontend | React 18 + Vite 5 + TailwindCSS 3 + Recharts |
| Backend | FastAPI (Python) |
| ML | PyTorch + HuggingFace Transformers + PhoBERT fine-tuned |
| Stylometry | scikit-learn (TF-IDF + cosine similarity) |
| Duplicate detection | datasketch (SimHash) |
| Scraping | Playwright (Google Maps), httpx + BeautifulSoup4 (Foody.vn) |
| Database | PostgreSQL 16 |
| Deploy | Docker Compose → Railway/Render |

---

## 7. Kế hoạch thực hiện theo Phase

### Phase 0 — Chuẩn bị & Nghiên cứu *(Tuần 1)*

| Việc làm | Output |
|----------|--------|
| Đọc papers chính (UIT 2022, UIT 2024, AiGen-FoodReview 2024) | Notes tóm tắt |
| Tải và explore datasets HuggingFace | EDA notebook |
| Setup môi trường: Python, CUDA, PostgreSQL, Node | Môi trường chạy được |
| Tạo cấu trúc thư mục dự án + init GitHub | Repo git |

### Phase 1 — Data & ML *(Tuần 2–4)*

| Tuần | Việc làm | Output |
|------|----------|--------|
| 2 | Merge datasets + scrape Google Maps + Foody + label + generate fake | Dataset files |
| 3 | Fine-tune PhoBERT (3–5 epochs, RTX 3060) | Model .pt |
| 4 | Ablation study: content only / +identity / +context / full 3-layer | Notebook + metrics |

**Chỉ tiêu:** F1 ≥ 0.83, ablation chứng minh 3-layer > 2-layer > 1-layer

### Phase 2 — Backend *(Tuần 5–6)*

| Tuần | Việc làm | Output |
|------|----------|--------|
| 5 | DB schema + Google Maps scraper + Foody scraper + async job | Scrapers chạy |
| 6 | Content Module + Identity Module + Context Module + Trust Engine | API endpoints |

### Phase 3 — Frontend *(Tuần 7–8)*

| Tuần | Việc làm | Output |
|------|----------|--------|
| 7 | Home + Restaurant dashboard (Void Score, Adjusted Rating, Archetypes, Timeline) | Dashboard |
| 8 | Analyze demo page + Top Trusted Reviews + Polish UI | Web app hoàn chỉnh |

### Phase 4 — Tích hợp & Kiểm thử *(Tuần 9)*

| Việc làm | Output |
|----------|--------|
| End-to-end test 5+ quán | Test report |
| Edge cases + error handling | Robust |
| Unit tests scoring engine (pytest) | tests/ |

### Phase 5 — Deploy & Báo cáo *(Tuần 10)*

| Việc làm | Output |
|----------|--------|
| Docker Compose + deploy Railway/Render | URL public |
| Báo cáo đồ án + slide demo | .docx + .pptx |

---

## 8. Cấu trúc báo cáo đồ án

```
Chương 1: Giới thiệu
  1.1 Đặt vấn đề
  1.2 Mục tiêu
  1.3 Phạm vi
  1.4 Bố cục báo cáo

Chương 2: Cơ sở lý thuyết
  2.1 Fake review detection — tổng quan
  2.2 PhoBERT và BERT fine-tuning
  2.3 Stylometry — nhận diện danh tính qua văn phong
  2.4 SimHash — locality sensitive hashing
  2.5 Cross-platform verification
  2.6 Các nghiên cứu liên quan

Chương 3: Dữ liệu
  3.1 Nguồn dữ liệu (HuggingFace + scrape + GPT)
  3.2 Thu thập và xử lý
  3.3 Cross-platform dataset (Google Maps × Foody)
  3.4 Thống kê mô tả + EDA

Chương 4: Phương pháp
  4.1 Kiến trúc 3-layer tổng thể
  4.2 Layer 1: Content — PhoBERT + rules
  4.3 Layer 2: Identity — Stylometry + credibility signals
  4.4 Layer 3: Context — Batch patterns + cross-platform
  4.5 Trust Score, Void Score, Adjusted Rating
  4.6 Reviewer Archetypes

Chương 5: Thực nghiệm
  5.1 Môi trường thực nghiệm
  5.2 Kết quả fine-tune PhoBERT
  5.3 Ablation study (1-layer vs 2-layer vs 3-layer)
  5.4 Cross-platform analysis
  5.5 Case study: phân tích 3–5 quán thực tế

Chương 6: Xây dựng hệ thống
  6.1 Kiến trúc phần mềm
  6.2 Backend (FastAPI)
  6.3 Frontend (React)
  6.4 Deploy

Chương 7: Kết luận
  7.1 Kết quả đạt được
  7.2 Hạn chế
  7.3 Hướng phát triển
```

---

## 9. Rủi ro và mitigation

| Rủi ro | Xác suất | Mitigation |
|--------|----------|------------|
| Google Maps block scraper | Cao | playwright-stealth + random delay + giới hạn 100 reviews/quán |
| Foody thay đổi HTML structure | Trung bình | BeautifulSoup selector dễ update + graceful fallback |
| Stylometry không đủ signal từ 1 batch | Trung bình | Dùng như bonus signal, không phải signal chính trong Identity |
| Dataset không đủ → F1 thấp | Trung bình | Tăng GPT-generated, điều chỉnh class weight |
| PhoBERT overfit | Thấp | Early stopping, validation loss monitoring |
| Deploy free tier thiếu RAM | Trung bình | Quantize model (int8), CPU inference |

---

## 10. Tài liệu tham khảo chính

1. Co Van Dinh, Son T. Luu et al. (2022). *Detecting Spam Reviews on Vietnamese E-commerce Websites.* arXiv:2207.14636
2. Co Van Dinh, Son T. Luu. (2024). *Metadata Integration for Spam Reviews Detection on Vietnamese E-commerce Websites.* arXiv:2405.13292
3. Alessandro Gambetti, Qiwei Han. (2024). *AiGen-FoodReview: A Multimodal Dataset of Machine-Generated Restaurant Reviews.* ICWSM 2024
4. Nguyen, D.Q., & Nguyen, A.T. (2020). *PhoBERT: Pre-trained language models for Vietnamese.* Findings of EMNLP 2020
5. Mukherjee, A. et al. (2013). *What Yelp Fake Review Filter Might Be Doing?* ICWSM 2013
6. Rayana, S., & Akoglu, L. (2015). *Collective Opinion Spam Detection.* KDD 2015
7. Koppel, M., & Schler, J. (2004). *Authorship verification as a one-class classification problem.* ICML 2004 — nền tảng stylometry
