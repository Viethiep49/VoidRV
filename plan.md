# VoidRV — Kế hoạch thực hiện dự án (Project Plan)

Dự án được chia thành 6 Phase (từ Phase 0 đến Phase 5) thực hiện trong vòng 10 tuần, tập trung vào việc xây dựng hệ thống **VoidRV** xác định độ tin cậy của review nhà hàng đa nền tảng, tích hợp Explainable AI (XAI) và Cluster Detection.

---

## ⏳ Phase 0: Chuẩn bị & Nghiên cứu (Tuần 1)

**Mục tiêu:** Nắm vững cơ sở lý thuyết, chuẩn bị sẵn sàng môi trường phát triển.

- [ ] **Nghiên cứu tài liệu:** Đọc các papers chính (UIT 2022, UIT 2024, AiGen-FoodReview 2024) về Fake Review Detection và kiến trúc PhoBERT.
- [ ] **Khảo sát dữ liệu:** Tải và explore các datasets có sẵn trên HuggingFace (ViSpamReviews, ViSpamDetection v2). Tạo EDA (Exploratory Data Analysis) notebook.
- [ ] **Setup môi trường:** Cài đặt Python, cấu hình CUDA cho PyTorch, PostgreSQL, và Node.js/Vite.
- [ ] **Khởi tạo dự án:** Thiết lập cấu trúc thư mục repo, init Git và đẩy lên GitHub.

**Output:** Notes tóm tắt lý thuyết, EDA notebook, Repo Git đã sẵn sàng.

---

## 🧠 Phase 1: Data & ML Pipeline (Tuần 2–4)

**Mục tiêu:** Xây dựng tập dữ liệu chất lượng cao và huấn luyện mô hình phân loại lõi.

- **Tuần 2:**
  - [ ] Xây dựng script scrape dữ liệu thô từ Google Maps và Foody (bằng Playwright và BeautifulSoup).
  - [ ] Gộp (Merge) datasets có sẵn và dữ liệu tự scrape.
  - [ ] Gán nhãn thủ công kết hợp sử dụng GPT để generate thêm các mẫu review giả (fake reviews) nhằm cân bằng dữ liệu.
- **Tuần 3:**
  - [ ] Fine-tune mô hình `vinai/phobert-base` cho bài toán Binary Classification (genuine vs fake) chuyên biệt cho domain F&B.
  - [ ] Đánh giá mô hình (đạt target F1 ≥ 0.83).
- **Tuần 4:**
  - [ ] Thực hiện Ablation Study để chứng minh hiệu quả của kiến trúc đa tầng (so sánh 1-layer vs 3-layer).

**Output:** Tập dataset hoàn chỉnh, File weights mô hình (`.pt`), Notebook chứa kết quả đánh giá và Ablation Study.

---

## ⚙️ Phase 2: Backend Development (Tuần 5–6)

**Mục tiêu:** Xây dựng các API lõi, các Scraper tự động và Trust Engine tích hợp XAI.

- **Tuần 5:**
  - [ ] Thiết kế và khởi tạo Database Schema (PostgreSQL với SQLAlchemy).
  - [ ] Hoàn thiện Hybrid Scraper: Tự động cào dữ liệu Google Maps qua URL.
  - [ ] Xây dựng module Entity Matching (khớp quán Google Maps với Foody dựa trên Fuzzy Matching và Geospatial).
- **Tuần 6:**
  - [ ] Xây dựng Core Trust Engine gộp điểm từ 3 layers (Content, Identity, Context).
  - [ ] Xây dựng thuật toán Cluster Detection (phát hiện hành vi nhóm/review rings).
  - [ ] Triển khai XAI Explainer: Tạo giải thích ngôn ngữ tự nhiên (Natural Language) cho Trust Score.
  - [ ] Hoàn thiện các REST API endpoints bằng FastAPI.

**Output:** API backend chạy ổn định, Scrapers và hệ thống đối chiếu đa nền tảng hoạt động tốt.

---

## 🖥️ Phase 3: Frontend Development (Tuần 7–8)

**Mục tiêu:** Xây dựng giao diện hướng người dùng (Traveler-centric), trực quan hóa các luồng dữ liệu phức tạp.

- **Tuần 7:**
  - [x] Dựng khung React/Vite app và kết nối với Backend API.
  - [x] Xây dựng Restaurant Dashboard tổng quan.
  - [x] Vẽ các biểu đồ: Inflation Gap Chart (so sánh rating GG vs Foody), Timeline review (phát hiện burst), Archetypes Pie Chart.
- **Tuần 8:**
  - [x] Xây dựng UI hiển thị chi tiết XAI Breakdown cho từng review.
  - [x] Xây dựng component hiển thị Top Trusted Reviews.
  - [x] Polish UI/UX, thêm các hiệu ứng loading (Scrape Progress) và hoàn thiện responsive.

**Output:** Web application hoàn chỉnh, người dùng có thể nhập URL và xem kết quả phân tích trực quan.

---

## 🧪 Phase 4: Tích hợp & Kiểm thử (Tuần 9)

**Mục tiêu:** Đảm bảo hệ thống hoạt động trơn tru từ đầu đến cuối và xử lý tốt các ngoại lệ.

- [ ] **Tích hợp End-to-end:** Test toàn bộ luồng từ lúc nhập URL -> Scrape -> Phân tích -> Trả kết quả lên UI.
- [ ] **Unit Tests:** Viết test cho các hàm tính điểm (Scoring logic) cốt lõi của Trust Engine.
- [ ] **Xử lý Edge Cases:** Quán không có trên Foody, URL Google Maps lỗi, timeout khi scrape, chống bị block IP.
- [ ] **Case Studies:** Chạy thử hệ thống với 5+ quán ăn thực tế (có dấu hiệu bị review farm) để thu thập kết quả cho báo cáo.

**Output:** Hệ thống robust, Test report chi tiết, Log kết quả của các Case Studies.

---

## 🚀 Phase 5: Deploy & Báo cáo (Tuần 10)

**Mục tiêu:** Đưa ứng dụng lên môi trường live và hoàn tất hồ sơ bảo vệ đồ án.

- [ ] **Triển khai (Deploy):** Đóng gói toàn bộ ứng dụng bằng Docker Compose. Deploy Backend/Frontend/DB lên cloud (Railway, Render hoặc VPS).
- [ ] **Báo cáo:** Viết file Báo cáo Đồ án chuyên ngành (.docx) dựa trên Proposal và kết quả thực nghiệm.
- [ ] **Slide Demo:** Chuẩn bị Slide thuyết trình (.pptx) và kịch bản demo trực tiếp cho Hội đồng.

**Output:** URL Public của ứng dụng, File Báo cáo và Slide thuyết trình hoàn chỉnh. Trang bị sẵn sàng cho buổi bảo vệ.