# ĐỀ CƯƠNG CHI TIẾT ĐỒ ÁN CHUYÊN NGÀNH

> **Sinh viên thực hiện:** Trương Viết Hiệp
> **MSSV:** 2380600637
> **Trường:** Đại học Công nghệ TP.HCM (HUTECH)
> **Khoa:** Công nghệ Thông tin — Hệ thống Thông tin Ứng dụng
> **Năm học:** 2025–2026
> **Giảng viên hướng dẫn:** *(Điền sau)*

---

## 1. TÊN ĐỀ TÀI

**VoidRV: Hệ thống xác định độ tin cậy review nhà hàng sử dụng phân tích nội dung (PhoBERT), nhận diện danh tính reviewer (Stylometry), và đối chiếu đa nền tảng (Google Maps × Foody)**

---

## 2. GIỚI THIỆU VÀ ĐẶT VẤN ĐỀ

### 2.1 Thực trạng và lý do chọn đề tài
Trong sự phát triển mạnh mẽ của ngành dịch vụ F&B (Food and Beverage) tại Việt Nam cùng với sự bùng nổ của du lịch tự túc, các đánh giá rà soát (online reviews) trên các nền tảng như Google Maps, Foody, hay TripAdvisor đã trở thành yếu tố sống còn quyết định sự thành bại của cơ sở kinh doanh và định hướng lựa chọn của thực khách.

Tuy nhiên, hệ sinh thái đánh giá trực tuyến đang bị thao túng nghiêm trọng bởi các vấn đề cốt lõi sau:
- **Ngành công nghiệp Review Farm:** Dịch vụ "tăng sao", "đẩy top" diễn ra công khai. Chỉ với vài trăm nghìn đồng, chủ quán có quyền mua hàng trăm lượt đánh giá 5 sao kèm bình luận có cánh.
- **Hiện tượng Review Bombing:** Các chiến dịch tấn công hội đồng (đánh 1 sao hàng loạt) vì những mâu thuẫn không liên quan đến chất lượng món ăn, phá hoại danh tiếng doanh nghiệp.
- **Tài khoản rác (Ghost accounts):** Các tài khoản vô danh được tự động hoá tạo ra chỉ nhằm mục đích farm rating.

Hiện nay, khi người dùng đọc một đánh giá trên Google Maps, họ không có bất kỳ công cụ đo lường nào hỗ trợ xác định xem: *"Đây là thực khách trải nghiệm thật hay là một bài đăng dịch vụ?"* Đề tài được đề xuất nhằm giải quyết trực tiếp nỗi đau (pain point) này của người sử dụng đầu cuối.

### 2.2 Tình hình nghiên cứu và khoảng trống (Research Gap)
Các nghiên cứu hiện tại về nhận diện Fake Review tại thị trường Việt Nam (điển hình như nhóm tác giả từ Đại học CNTT (UIT) năm 2022 và 2024) tập trung chủ yếu vào miền dữ liệu **Thương mại điện tử (Tiki, Shopee)**. Cụ thể:
- Các hệ thống trước đó chỉ dựa vào sự kết hợp giữa xử lý ngôn ngữ NLP cơ bản và metadata trang cá nhân, không có tính đa nền tảng.
- Miền dữ liệu F&B (Nhà hàng, quán ăn) với ngữ cảnh đánh giá mang tính chất địa lý đặc thù và cảm tính cao vẫn đang là một khoảng trống nghiên cứu lớn tại thị trường trong nước.

### 2.3 Câu hỏi nghiên cứu
1. Làm thế nào để xây dựng một kiến trúc trí tuệ nhân tạo có năng lực kết hợp nội dung văn bản (Content), danh tính ẩn (Identity) và bối cảnh (Context) nhằm đánh giá độ tin cậy một review?
2. Có thể phân tích sự chênh lệch (Gap) giữa Google Maps và một nền tảng bản địa như Foody.vn để sử dụng làm chỉ dấu xác thực hành vi lạm phát đánh giá (Rating Inflation) không?
3. Các hành vi thao túng review thường có cấu trúc và tần suất như thế nào? (Temporal clusters).

---

## 3. MỤC TIÊU VÀ PHẠM VI NGHIÊN CỨU

### 3.1 Mục tiêu tổng quát
Xây dựng một hệ thống phần mềm (Web Application) tự động trích xuất, phân tích và cho ra kết quả định lượng về "Độ đáng tin cậy" (Trust Score) của một hàng quán dựa trên đường dẫn Google Maps do người dùng cung cấp. Hệ thống được trợ lực bởi AI và phân tích phân cụm cung cấp góc nhìn đa chiều về chất lượng thực sự của nhà hàng.

### 3.2 Mục tiêu cụ thể
1. **Xây dựng Data Pipeline:** Tự động hoá thu thập dữ liệu review từ đường dẫn Google Maps và module đối soát chéo (Entity Matching) tự động tìm kiếm quán đó trên Foody.
2. **Nghiên cứu & Huấn luyện Model NLP:** Fine-tune mô hình ngôn ngữ lớn PhoBERT với dữ liệu F&B chuyên ngành đạt chỉ số độ chính xác (F1-score) > 80% trong việc phân loại review chân thật và review đáng ngờ.
3. **Triển khai Identity Engine (Stylometry):** Áp dụng kỹ thuật phân tích văn phong (Stylometry) sử dụng TF-IDF và N-gram để nhận diện các dấu vết "sản xuất hàng loạt" của các bài tập review copy-paste.
4. **Phát triển thuật toán phát hiện bất thường:** Nhóm các review theo mốc thời gian (Temporal Clustering) và tính toán khoảng cách vector nhằm phát hiện hành vi thả sao hàng loạt.
5. **Xây dựng ứng dụng hoàn chỉnh:** Frontend Trực Quan (Dashboard) thể hiện Điểm hiệu chỉnh (Adjusted Rating), các bình luận đáng tin nhất và lý giải AI. Bệ phóng phục vụ người dùng chuẩn bị quyết định đến ăn.

### 3.3 Phạm vi nghiên cứu
- **Giới hạn miền ứng dụng:** Đồ án tập trung giới hạn trên miền nhà hàng, ẩm thực, thức uống tại thị trường Việt Nam bằng tiếng Việt.
- **Giới hạn nền tảng thu thập:** Dữ liệu nguồn chủ đạo từ Google Maps, đối soát với nền tảng Foody.vn.
- **Giới hạn thuật toán:** Tập trung Phân tích văn bản (NLP) + Hành vi thời gian. (Tạm gác lại chức năng Xử lý ảnh chụp để giới hạn khối lượng cho đồ án chuyên ngành).

---

## 4. HƯỚNG TIẾP CẬN VÀ PHƯƠNG PHÁP NGHIÊN CỨU

### 4.1 Phương pháp thu thập dữ liệu (Scraping & Aggregation)
Hệ thống sử dụng Bot tự động hoá (Playwright - Headless Browser) đóng giả người dùng truy xuất dữ liệu động (Dynamic DOM) từ Google Maps, sau đó truyền thông tin tên quán và toạ độ đi tìm kiếm chéo trên trang Foody.vn thông qua matching thuật toán Levenshtein Distance & Toạ độ địa lý (Haversine Formula).

### 4.2 Cấu trúc phân tích đa tầng (VoidRV 3-Layer Architecture)
Sự độc đáo của đồ án nằm ở thuật toán Void Trust Engine chấm điểm qua 3 lăng kính đánh giá song song trước khi tổng hợp ra điểm cuối cùng:

- **Layer 1: Content Intelligence (Phân tích nội dung NLP - 40% trọng số)**
  Sử dụng pre-trained model **PhoBERT** của VinAI, fine-tune lại với tập dữ liệu spam/genuine review. Layer này xử lý cảm xúc (sentiment), bóc tách thực thể (Mention món ăn, giá cả cụ thể - NER) và tìm sự phi logic giữa số sao với nội dung text.
  
- **Layer 2: Stylometry & Identity Profiling (Nhận diện văn phong không profile - 30% trọng số)**
  Tài khoản Reviewer rác thường có văn phong đồng nhất. Hệ thống phân tích tần suất ký tự, quy tắc dấu câu, cấu trúc n-gram để vẽ ra một "vân tay ngôn ngữ". Từ đó phát hiện cụm các tài khoản khác nhau nhưng cùng chung "một người nhấn phím".
  
- **Layer 3: Bối cảnh và Thống kê tần số (Context & Forensics - 30% trọng số)**
  Phân tích biểu đồ thời gian gia tăng review (Time-series analysis). Nếu có khối lượng nhận xét tăng đột biến 500% trong 2 tuần mà không nằm trong dịp lễ/sale thì hệ thống ghi nhận rủi ro Review Farm/Bombing.

---

## 5. CÔNG NGHỆ SỬ DỤNG (TECH STACK)

1. **AI / Xử lý phân tích dữ liệu:** 
   - Framework: `PyTorch`, `HuggingFace Transformers`.
   - Thuật toán NLP: `PhoBERT`, Sentiment Analysis, NER.
   - Thống kê / Machine Learning: `scikit-learn` (DBSCAN Clustering, TF-IDF), thuật toán đối chiếu dữ liệu `SimHash` (Datasketch).
2. **Backend Services & Scraping:**
   - Framework API: `FastAPI` (Python). Tốc độ cao và tối ưu cho bất đồng bộ (ASync).
   - Scraping Engine: `Playwright`, `BeautifulSoup4`.
3. **Database:** 
   - Hệ quản trị CSDL quan hệ: `PostgreSQL` dành cho lưu trữ phân tích kết quả lâu dài.
4. **Trình bao biểu Diễn (Frontend):** 
   - Thư viện Web: `React 18` + `Vite` + `TailwindCSS` tạo Dashboard UI trực quan. Biểu đồ dữ liệu dùng `Recharts`.
5. **Vận hành (Deployment):** 
   - `Docker`, Hosting lên hạ tầng đám mây `Railway` hoặc `Render`.

---

## 6. KẾ HOẠCH THỰC HIỆN DỰ KIẾN (TIMELINE 12 TUẦN)

| Thời gian | Hạng mục công việc yếu điểm | Kết quả báo cáo (Deliverables) |
|---|---|---|
| **Tuần 1 - 2** | Khảo sát nghiên cứu các Paper liên quan, cấu trúc thiết kế CSDL và luồng Architecture. Môi trường setup hoàn tất. | Design Spec, Sơ đồ cơ sở dữ liệu. |
| **Tuần 3 - 4** | Xây dựng Scrapping Tools cho Google Maps, Foody. Thu thập tập dữ liệu mẫu. Tiền xử lý dữ liệu NLP tiếng Việt. | Dataset đầu vào làm sạch (~5000 records). |
| **Tuần 5 - 6** | Huấn luyện mô hình PhoBERT (Fine-tuning classification); Triển khai Stylometry và Thuật toán đối chiếu SimHash. | Khối mô hình ML được export .pt. Score Metrics báo cáo được F1 > 0.8. |
| **Tuần 7 - 8** | Xây dựng cụm server API FastAPI với Async request để xử lý model tính toán Trust Engine. | Docs API hoàn chỉnh và chạy thực nghiệm postman. |
| **Tuần 9 - 10** | Trình diễn giao diện Front-end, biểu đồ trực quan, Dashboard tích hợp biểu tượng Void Score. | Giao diện Web Application SPA có thể truy cập được. |
| **Tuần 11 - 12** | Test Case toàn hệ thống End-to-End, Fix lỗi, Đóng gói Docker, Viết Báo cáo Luận văn. In quyển. | Bản báo cáo giấy, file source code đầy đủ bàn giao. |

---

## 7. CẤU TRÚC QUYỂN BÁO CÁO DỰ KIẾN

- **MỞ ĐẦU:** Tính cấp thiết, mục tiêu, đối tượng, phương pháp và ý nghĩa đề tài.
- **CHƯƠNG 1: TỔNG QUAN VỀ HỆ THỐNG GỢI Ý VÀ SPAM REVIEW:** Các nền tảng F&B, review farm, fake reviews, lý thuyết về kiến trúc hệ thống hiện hành.
- **CHƯƠNG 2: CƠ SỞ LÝ THUYẾT:** Các thuật toán Machine Learning sử dụng: PhoBERT, tf-idf, biểu diễn văn phong (Stylometry), NLP căn bản cho tiếng Việt, Kỹ thuật crawl dữ liệu.
- **CHƯƠNG 3: MÔ HÌNH VOIDRV & DATASET:** Kiến trúc giải pháp 3 lớp thông minh. Phân tích tập dữ liệu tự thu thập, quá trình dán nhãn (label).
- **CHƯƠNG 4: THUẬT TOÁN & ĐÁNH GIÁ MÔ HÌNH VÀ THỰC NGHIỆM:** Các kết quả thực nghiệm fine-tuning, Precision, Recall và thông số chứng minh tính khách quan của thuật toán.
- **CHƯƠNG 5: PHÁT TRIỂN ỨNG DỤNG WEB:** Giới thiệu UX/UI, chức năng Web Application dành cho khách du lịch/trải nghiệm.
- **KẾT LUẬN & HƯỚNG PHÁT TRIỂN TƯƠNG LAI.**
- **TÀI LIỆU THAM KHẢO.**

---

## 8. DỰ KIẾN RỦI RO VÀ GIẢI PHÁP PHÒNG NGỪA

1. **Rủi ro API/Scraping bị chặn (Rate Limit / Captcha):** Các cổng Google Maps thường thắt chặt lấy dữ liệu tự động.
   → *Biện pháp:* Dùng Playwright ẩn danh chặn resource không cần thiết (Ảnh, Ads), random proxy timing, giả dạng User-Agent.
2. **Tập dữ liệu thiếu nhầm (Imbalanced Label):** Các nhận xét ở hệ thống là dữ liệu trơn không có nhãn sẵn. 
   → *Biện pháp:* Tự gán nhãn thủ công (Manual Labeling) theo luật Heuristics bằng việc trích mẫu ngẫu nhiên (Random Sampling) hoặc sử dụng LLMs như GPT-4 trợ sức generate dữ liệu label chuẩn.
3. **Model size quá lớn để Deploy chạy Web server Free:** PhoBERT khá to so với Cloud thông thường có RAM hạn hẹp.
   → *Biện pháp:* Export ra định dạng ONNX tăng tốc độ truy xuất, hoặc dùng mô hình phân lớp nhẹ hơn, chạy dạng async task offline.
   
---

## 9. TÀI LIỆU THAM KHẢO

[1] Co Van Dinh, Son T. Luu et al. (2022). *Detecting Spam Reviews on Vietnamese E-commerce Websites.* arXiv:2207.14636
[2] Co Van Dinh, Son T. Luu. (2024). *Metadata Integration for Spam Reviews Detection on Vietnamese E-commerce Websites.* arXiv:2405.13292
[3] Alessandro Gambetti, Qiwei Han. (2024). *AiGen-FoodReview: A Multimodal Dataset of Machine-Generated Restaurant Reviews.* ICWSM 2024
[4] Nguyen, D.Q., & Nguyen, A.T. (2020). *PhoBERT: Pre-trained language models for Vietnamese.* Findings of EMNLP 2020
[5] Rayana, S., & Akoglu, L. (2015). *Collective Opinion Spam Detection.* KDD 2015
[6] Tài liệu kỹ thuật HuggingFace, FastAPI, ReactJS.
