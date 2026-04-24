# ĐỀ CƯƠNG CHI TIẾT ĐỒ ÁN CHUYÊN NGÀNH

> **Sinh viên thực hiện:** Trương Viết Hiệp
> **MSSV:** 2380600637
> **Trường:** Đại học Công nghệ TP.HCM (HUTECH)
> **Khoa:** Công nghệ Thông tin — chuyên ngành Hệ thống Thông tin Ứng dụng
> **Năm học:** 2025–2026
> **Giảng viên hướng dẫn:** *(Điền sau)*

---

## 1. TÊN ĐỀ TÀI

**ReviewTrust (VoidRV): Hệ thống xác định độ tin cậy review nhà hàng tiếng Việt dựa trên kiến trúc kết hợp đặc trưng văn bản (PhoBERT) và đặc trưng hành vi reviewer (behavioral features).**

---

## 2. GIỚI THIỆU VÀ ĐẶT VẤN ĐỀ

### 2.1. Thực trạng

Ngành F&B (Food & Beverage) tại Việt Nam đang phát triển mạnh mẽ cùng với sự bùng nổ của du lịch tự túc. Các nền tảng đánh giá trực tuyến như **Google Maps**, **Foody.vn**, **TripAdvisor** đã trở thành kênh tham khảo chủ đạo của thực khách trước khi lựa chọn nhà hàng. Tuy nhiên, hệ sinh thái review hiện đang bị thao túng bởi nhiều vấn đề:

- **Review farm:** dịch vụ "tăng sao", "đẩy top" diễn ra công khai; chỉ vài trăm nghìn đồng, chủ quán có thể mua hàng trăm review 5 sao kèm bình luận có cánh.
- **Review bombing:** chiến dịch đánh 1 sao hàng loạt vì mâu thuẫn không liên quan đến chất lượng món ăn, phá hoại danh tiếng doanh nghiệp.
- **Ghost accounts / tài khoản rác:** tài khoản vô danh được tạo hàng loạt nhằm farm rating.
- **Review do AI sinh (GAI-generated):** từ 2023 trở đi, lượng fake review được sinh bởi ChatGPT/LLM tăng đột biến; nghiên cứu mới (Luo et al., 2026 — *Decision Support Systems*) chỉ ra đây là mối đe doạ cấp bách mới nổi lên trong hệ sinh thái review.
- **Review generic không chứa thông tin:** "Ngon lắm!", "Tuyệt vời!"… — không có giá trị tham khảo nhưng vẫn tính vào rating trung bình.

Theo báo cáo của chính phủ Anh (2023) được trích dẫn trong Xu & Huo (2026), fake review gây thiệt hại cho người tiêu dùng £500 triệu – £3,1 tỷ/năm. TripAdvisor báo cáo đã phát hiện 1,3 triệu fake review chỉ trong năm 2022.

### 2.2. Bài toán cần giải quyết

> **Bài toán:** Cho một review nhà hàng (văn bản tiếng Việt + số sao + metadata reviewer + thời điểm đăng), hãy đưa ra một **Trust Score** định lượng trong thang 0–100 và một **nhãn phân loại** (Đáng tin cậy / Cần thận trọng / Nghi ngờ), kèm **danh sách lý do giải thích** (explainable) cho quyết định đó. Đồng thời, với mức nhà hàng, hệ thống tổng hợp các Trust Score review thành **Adjusted Rating** (rating thật sau khi lọc review đáng ngờ).

Đây là **bài toán phân loại nhị phân (fake/genuine) có gắn điểm tin cậy liên tục và có lời giải thích** — ở giao điểm của ba lĩnh vực: Fake Review Detection (FRD), NLP tiếng Việt, và Explainable AI.

### 2.3. Phạm vi ứng dụng

| Trục phạm vi | Trong phạm vi đồ án | Ngoài phạm vi (defer) |
|-------------|--------------------|----------------------|
| **Ngôn ngữ** | Tiếng Việt | Tiếng Anh, đa ngôn ngữ |
| **Miền (domain)** | Nhà hàng / quán ăn / quán nước | Khách sạn, E-commerce (Shopee, Tiki) |
| **Nguồn dữ liệu** | Google Maps (chính); Foody.vn (bổ sung) | TripAdvisor, Yelp, Facebook |
| **Modality** | Văn bản + metadata số (text + numerical) | Ảnh (CV), Video, Audio, GPS |
| **Hình thức sản phẩm** | Web Application (SPA) | Mobile app, browser extension |
| **Nghiệp vụ** | Phân tích độ tin cậy + dashboard quán | Kiểm duyệt tự động, báo cáo vi phạm |

### 2.4. Lý do chọn đề tài

1. **Tính cấp thiết thực tiễn:** Người tiêu dùng Việt Nam hiện **không có công cụ nào** giúp đánh giá độ tin cậy của từng review Google Maps — một "nỗi đau" cụ thể, rõ ràng.
2. **Khoảng trống nghiên cứu:** Các nghiên cứu FRD tiếng Việt hiện có (nhóm UIT 2022, 2024) đều tập trung miền **e-commerce** (Tiki, Shopee). Miền **F&B tiếng Việt** với ngữ cảnh địa lý, cảm tính cao vẫn là một khoảng trống (chi tiết tại mục 3).
3. **Khả thi về kỹ thuật:** PhoBERT (VinAI) đã được pre-train mạnh cho tiếng Việt, fine-tune cho binary classification là khả thi với cấu hình cá nhân (RTX 3060 12GB).
4. **Phù hợp chuyên ngành Hệ thống Thông tin Ứng dụng:** đồ án tích hợp **ML pipeline + Web application + Database + API design** — đúng chuyên ngành HTTTUD.
5. **Khả thi về dữ liệu:** Google Maps là nguồn công khai, có thể scrape hợp pháp bằng Playwright (ở quy mô nhỏ cho mục đích nghiên cứu học thuật).

---

## 3. HIỆN TRẠNG BÀI TOÁN VÀ KHẢO SÁT NGHIÊN CỨU LIÊN QUAN

### 3.1. Dòng chảy nghiên cứu Fake Review Detection

Bài toán FRD bắt đầu từ công trình tiên phong của **Jindal & Liu (2008)** — định nghĩa 3 loại opinion spam (untruthful / brand-only / non-review) và đặt nền móng bằng Logistic Regression trên đặc trưng duplicate content. Từ đó đến nay, giới nghiên cứu đã trải qua 4 giai đoạn:

| Giai đoạn | Hướng chủ đạo | Đại diện |
|-----------|--------------|----------|
| 2008–2013 | Linguistic features + ML cổ điển (SVM, LR, NB) | Jindal & Liu (2008); Ott et al. (2011) |
| 2013–2017 | Behavior features + Graph-based | Mukherjee et al. (2013); Rayana & Akoglu (2015) — SpEagle |
| 2017–2022 | Deep Learning (CNN, LSTM, BERT) + Multi-feature fusion | Shehnepoor et al. (NetSpam); Barbado et al. |
| 2023–2026 | LLM-generated review detection + Multimodal + Human-in-the-loop | Luo et al. (2026); Xu & Huo (2026); Mewada & Dewang (2026) |

### 3.2. Các nghiên cứu quốc tế tiêu biểu (khảo sát 5 paper SCI/SCIE 2025–2026)

#### (1) Luo, Nan & Li (2026) — AI-generated Fake Review Detection
*Decision Support Systems* (2026).

- **Vấn đề:** LLM (ChatGPT, Gemini) sinh fake review hàng loạt, khó phân biệt bằng mắt thường.
- **Phương pháp:** Xây dựng 2 loại biến (linguistic: perplexity, burstiness; emotional: cường độ cảm xúc) → áp dụng Outlier Detection dựa trên Cumulative Probability Density → huấn luyện AdaBoost phân loại.
- **Kết quả:** Vượt nhiều baseline state-of-the-art trên dữ liệu e-commerce.
- **Hạn chế:** Chỉ thực nghiệm tiếng Anh; cần dữ liệu có nhãn; chưa xét yếu tố behavior (reviewer history).

#### (2) Zhang, Ngai, Xia & Wu (2025) — DCOC: Dynamic Classification for Online Content
*Knowledge-Based Systems* (2025).

- **Vấn đề:** Dữ liệu review là dòng stream (streaming) liên tục, thay đổi theo thời gian, có nhiễu cao.
- **Phương pháp:** Kernel-based online learning với **slope-adjusted ramp loss** chống nhiễu; học incremental không cần retrain toàn bộ.
- **Kết quả:** Giữ độ chính xác ngay cả khi 30% dữ liệu bị nhiễu; thực nghiệm trên TripAdvisor, Yelp, Amazon.
- **Hạn chế:** Không phân tích nội dung sâu bằng transformer; phụ thuộc kernel function phải chọn thủ công.

#### (3) Qi, Li, Yang & Li (2025) — Transfer Learning for Fake News Detection (Survey)
*Information Fusion* (2025).

- **Đóng góp:** Hệ thống hoá transfer learning trong FRD thành 3 loại: cross-domain, domain adaptation, domain generalization.
- **Phát hiện quan trọng:** (i) Lớp nhãn mất cân bằng nghiêm trọng (fake:genuine ≈ 1:300 trong thực tế); (ii) Seesaw effect khi transfer cross-domain; (iii) **Low-resource languages như tiếng Việt gặp degradation mạnh** khi dùng model train trên tiếng Anh/Trung.
- **Gợi ý:** Khi làm bài toán FRD cho ngôn ngữ ít tài nguyên → **phải fine-tune lại trên dữ liệu bản địa**, không thể dùng model ngoại ngữ trực tiếp.

#### (4) Xu & Huo (2026) — IFML: Interpretable FRD với Multimodal + Human-Computer Collaboration
*Applied Soft Computing* (2026).

- **Phương pháp:** Kết hợp (a) **Multimodal VAE** (MVAE) fuse text + ảnh + đặc trưng cấu trúc; (b) **LLM** sinh giải thích tự nhiên (why fake?); (c) Bayesian framework kết hợp quyết định máy + feedback người dùng.
- **Kết quả:** PR AUC 94,43% trên 3 bộ Yelp; tăng 2,55% so với baseline tốt nhất.
- **Điểm đáng học:** (i) **Interpretability là bắt buộc** — người dùng không chỉ cần "fake/genuine" mà cần "vì sao"; (ii) contextual details càng phong phú → xác suất fake càng thấp; (iii) human-in-the-loop tăng độ chính xác đáng kể.
- **Hạn chế:** Yêu cầu dữ liệu đa phương thức (ảnh) không phải lúc nào cũng có sẵn; LLM API tốn chi phí runtime.

#### (5) Mewada & Dewang (2026) — ConvRoBERTa: Fusing Sequential + Weighted Nonsequential Features
*IEEE Transactions on Artificial Intelligence* (2026).

- **Vấn đề cốt lõi:** Các model trước (CNN-LSTM, DeceptiveBERT) chỉ dùng linguistic, **bỏ qua behavioral**; hoặc gán trọng số bằng nhau cho mọi đặc trưng.
- **Phương pháp:** (a) Dùng **CART** tính feature importance cho đặc trưng nonsequential (behavior metadata); (b) CNN trên các feature đã weighted; (c) RoBERTa encode text; (d) **Scaled dot-product attention** fuse cả hai.
- **Kết quả:** Accuracy **91,93%** trên Yelp (ConvRoBERTa-SVM), vượt baseline 2,94%.
- **Điểm đáng học (critical):** Đây là **phương pháp mạnh nhất và gần nhất với bài toán của chúng ta** — vì (i) fuse sequential + nonsequential giống 2-layer architecture; (ii) có cơ chế weighting cho feature quan trọng; (iii) phát hiện burstiness.
- **Hạn chế áp dụng trực tiếp:** Dùng RoBERTa (tiếng Anh); bỏ qua giải thích tự nhiên; chưa kiểm tra trên tiếng Việt / F&B.

### 3.3. Các nghiên cứu tại Việt Nam

| Năm | Tác giả | Miền | Phương pháp | Kết quả | Hạn chế |
|-----|---------|------|-------------|---------|---------|
| 2022 | Dinh, Luu et al. (UIT) | E-commerce (Shopee, Tiki, Lazada) | PhoBERT fine-tune + rules | F1 ≈ 0.78 | Chỉ text, không behavior; e-commerce không phải F&B |
| 2024 | Dinh, Luu (UIT) | E-commerce | PhoBERT + metadata integration | F1 ≈ 0.82 | Vẫn chỉ e-commerce; metadata đơn giản |
| 2020 | Nguyen & Nguyen (VinAI) | Nền tảng NLP chung | Pre-train PhoBERT-base 20GB | SOTA NER, POS, DP tiếng Việt | Không dành riêng cho FRD |

### 3.4. Bảng tổng hợp và phân tích hạn chế

| Phương pháp | Năm | Đặc trưng | F1/Acc | Hạn chế với bài toán của chúng ta |
|-------------|-----|-----------|--------|----------------------------------|
| Jindal & Liu (LR + duplicate) | 2008 | Linguistic only | ~0.65 | Không bắt được spam tinh vi |
| Ott et al. (SVM + n-gram) | 2011 | Linguistic | ~0.86* | *Chỉ trên domain hotel có crowd-sourced data |
| NetSpam (heterogeneous graph) | 2017 | Graph + metadata | ~0.89 | Yêu cầu graph review network lớn |
| DeceptiveBERT | 2022 | Contextual text | ~0.88 | Bỏ qua behavioral |
| **ConvRoBERTa** (Mewada 2026) | **2026** | **Text + behavior fuse + attention** | **91.93%** | Tiếng Anh, chưa F&B VN |
| IFML (Xu 2026) | 2026 | Multimodal + LLM + Bayesian | 94.43% PR-AUC | Yêu cầu ảnh; runtime LLM đắt |
| DCOC (Zhang 2025) | 2025 | Online streaming + robust loss | ~0.87 | Không dùng transformer |
| Luo (AdaBoost + outlier) | 2026 | AI-generated detection | SOTA | Tiếng Anh, không có behavior |
| UIT Vietnamese (Dinh 2024) | 2024 | PhoBERT + metadata | ~0.82 | E-commerce, không F&B |

### 3.5. Khoảng trống nghiên cứu (Research Gap)

Từ khảo sát trên, xác định 4 khoảng trống rõ ràng:

1. **Ngôn ngữ × Miền chưa được phủ:** Chưa có công trình nào công bố mô hình FRD riêng cho **tiếng Việt + miền F&B**.
2. **Khai thác đồng thời Content + Behavior còn hạn chế trong các nghiên cứu VN:** Dinh (2024) có metadata nhưng đơn giản; Mewada (2026) có fuse nhưng tiếng Anh.
3. **Thiếu khả năng giải thích (XAI):** Hầu hết model Vietnamese FRD chỉ trả về label, không có "vì sao". Xu & Huo (2026) đã chứng minh XAI tăng trust người dùng nhưng chưa có cho tiếng Việt.
4. **Thiếu sản phẩm đầu-cuối cho end-user:** Các paper chỉ dừng ở model, không có web app cho người dùng cuối (traveler) dùng trực tiếp.

### 3.6. Phương pháp kế thừa và hướng phát triển

**→ Phương pháp được kế thừa làm nền: ConvRoBERTa (Mewada & Dewang, 2026).**

**Lý do chọn:**
- (i) Là công trình 2026 mới nhất, trên tạp chí IEEE TAI uy tín.
- (ii) Kiến trúc fuse **sequential (text) + nonsequential (behavior)** khớp hoàn toàn với 2-layer architecture chúng ta đang thiết kế.
- (iii) Có cơ chế **feature weighting** (CART) cho feature quan trọng → giải quyết đúng hạn chế "treat all features equally" mà chính paper chỉ ra.
- (iv) Kết quả 91,93% đủ mạnh để làm baseline đáng tin.

**Hướng phát triển (đóng góp mới):**

| Thành phần kế thừa ConvRoBERTa | Thay đổi / mở rộng của ReviewTrust |
|-------------------------------|------------------------------------|
| RoBERTa encoder | **PhoBERT-base** (VinAI) cho tiếng Việt |
| Dataset Yelp (tiếng Anh) | **Dataset tự xây: Google Maps + Foody miền F&B VN** |
| Weighting = CART | Rule-based scoring + fine-tuned weight (đơn giản hơn, dễ giải thích hơn) |
| Attention fusion | **Linear combination có trọng số 0.6 × Content + 0.4 × Behavior** (đủ dùng cho scale SV, dễ debug) |
| Không có giải thích | **XAI Explainer** sinh danh sách lý do cho mỗi review (kế thừa idea của Xu & Huo 2026 nhưng dùng rule-based thay vì LLM để tiết kiệm chi phí) |
| Không có UI | **Web app React dashboard** có Trust Gauge, Adjusted Rating, Suspicious Cluster view |
| Không xét copy-paste | Bổ sung **SimHash** phát hiện review copy-paste (kế thừa từ Rayana & Akoglu 2015) |
| Không xét burst | Bổ sung **Burst detection** (≥ 15 tài khoản mới cùng ngày → cờ đỏ) |

> **Tóm lại:** Chúng ta **kế thừa triết lý fuse Content + Behavior từ ConvRoBERTa**, **thay RoBERTa bằng PhoBERT** cho tiếng Việt, **thay attention phức tạp bằng linear combination + rules** cho phù hợp quy mô đồ án chuyên ngành, và **bổ sung XAI + Web app** cho người dùng cuối.

---

## 4. NGUỒN DỮ LIỆU VÀ CHIẾN LƯỢC XÂY DỰNG TẬP DỮ LIỆU

### 4.1. Nguồn dữ liệu

| Nguồn | Hình thức thu thập | Dự kiến số lượng | Vai trò trong thực nghiệm |
|-------|-------------------|------------------|--------------------------|
| **Google Maps** | Playwright headless browser scrape các quán ăn HCM/HN | ~1.500–2.000 review | Tập **chính** — train/val/test fine-tune PhoBERT |
| **Foody.vn** | BeautifulSoup + HTML parsing | ~500–800 review | Tập **bổ sung** — tăng đa dạng văn phong bản địa |
| **LLM-generated (ChatGPT / Gemini)** | Prompt tạo review fake theo template | ~400–600 review | **Augment fake class** để cân bằng nhãn |
| **Dataset công khai (Ott 2011 / Yelp Chi 2013)** | Tải về, dịch sang tiếng Việt bằng Google Translate + rà soát thủ công | ~300 review | **Transfer cross-lingual** ban đầu |

**Tổng dự kiến: 2.700–3.700 review có nhãn.**

### 4.2. Quy trình thu thập

**Bước 1 — Chọn mẫu quán ăn.**

- Chọn 30–50 nhà hàng tại TP.HCM và Hà Nội, đa dạng:
  - Loại hình: quán phở, trà sữa, bún bò, nhà hàng buffet, quán cà phê, quán chay, quán nướng.
  - Cấp độ: từ quán vỉa hè đến nhà hàng cao cấp (để có đa dạng mức rating).
  - Số review: chỉ chọn quán có ≥ 30 review để đảm bảo đủ dữ liệu phân tích hành vi.

**Bước 2 — Scrape Google Maps.**

- Dùng `Playwright` + Chromium headless, random User-Agent, delay 2–5s giữa các request để tránh rate limit.
- Mỗi review thu thập: `content` (text), `star_rating`, `reviewer_name`, `reviewer_review_count`, `reviewer_photo` (optional), `posted_at`, `language`.
- Bỏ qua review không phải tiếng Việt (`language != "vi"`).

**Bước 3 — Scrape Foody.vn.**

- Dùng `BeautifulSoup` trên trang HTML tĩnh, không cần headless browser.
- Thu thập cùng schema để có thể join 2 nguồn.

**Bước 4 — Tiền xử lý.**

- Làm sạch text: loại bỏ emoji thừa, URL, @mention, chuẩn hoá dấu câu, normalise Unicode NFC.
- Word-segmentation bằng `pyvi` hoặc `underthesea` (chuẩn đầu vào cho PhoBERT — PhoBERT yêu cầu text đã tách từ).
- Tính SimHash 64-bit cho mỗi review để phát hiện duplicate.

### 4.3. Chiến lược gán nhãn (Data Labeling)

Đây là khâu **quan trọng nhất** vì dataset không có nhãn sẵn. Áp dụng chiến lược **Hybrid Labeling 3 tầng**:

#### Tầng 1 — Heuristic Rules (gán nhãn tự động sơ bộ)

Áp dụng luật heuristic để gán nhãn khởi tạo:

| Luật | Nhãn gợi ý |
|------|-----------|
| Review < 5 từ hoặc toàn emoji | **fake / low-quality** |
| Reviewer có < 3 review đời + đăng trong 1 giờ với review 5★ toàn quán cùng khu | **fake (farm pattern)** |
| SimHash similarity > 90% với ≥ 2 review khác trên platform | **fake (copy-paste)** |
| Sentiment (pyvi/PhoBERT sentiment) tích cực mạnh **đối lập** với rating ≤ 2 sao (hoặc ngược lại) | **fake (suspicious)** |
| Review có ≥ 3 aspects (đồ ăn, giá, dịch vụ, không gian) + ≥ 50 từ + reviewer có ≥ 10 review đa dạng | **genuine (strong)** |
| Nằm trong burst day (≥ 15 tài khoản mới cùng ngày, ≥ 5★) | **fake (burst)** |

#### Tầng 2 — LLM-assisted Labeling (Luo et al. 2026 gợi ý)

- Random sample ~30% tập dữ liệu, dùng GPT-4 / Gemini với prompt:

  > *"Đây là một review nhà hàng tiếng Việt. Hãy phân tích: (1) Nội dung có cụ thể không (đề cập món, giá, không gian)? (2) Có dấu hiệu AI-generated (câu quá mượt, công thức)? (3) Nhãn: genuine hay fake? Giải thích ngắn gọn."*

- Kết quả LLM dùng để **cross-check** với heuristic tầng 1. Nếu khớp → giữ nhãn; nếu lệch → chuyển tầng 3.

#### Tầng 3 — Manual Review (người gán nhãn chuẩn)

- SV tự gán nhãn thủ công **100% tập test (~500 review)** và **phần LLM/rule mâu thuẫn (~300–500 review)**.
- Quy tắc: 1 review được ≥ 2 lần review độc lập (SV + LLM) → dùng làm **gold label**.
- Tính **Cohen's Kappa** giữa heuristic/LLM/manual để báo cáo độ tin cậy gán nhãn (kỳ vọng κ ≥ 0.70 — "substantial agreement").

### 4.4. Đặc điểm và thống kê dự kiến của tập dữ liệu

| Thuộc tính | Giá trị dự kiến |
|-----------|-----------------|
| Tổng số review | ~3.000 |
| Số quán | 30–50 |
| Phân bố nhãn | fake ~35% / genuine ~65% (imbalanced nhẹ) |
| Độ dài trung bình | 25–40 từ |
| % review có aspect cụ thể | ~60% |
| % review có reviewer metadata đầy đủ | ~90% |
| Chia train/val/test | 70% / 15% / 15% |

**Tập dữ liệu sẽ được công bố công khai** (tùy chính sách Google Maps TOS — nếu không thể public full text thì công bố dạng anonymized + hash).

---

## 5. MỤC TIÊU NGHIÊN CỨU

### 5.1. Mục tiêu chung

> **Xây dựng và thực nghiệm một hệ thống web (Web Application) có khả năng tự động đánh giá độ tin cậy của review nhà hàng tiếng Việt bằng cách kết hợp phân tích nội dung (PhoBERT + rules) và phân tích hành vi reviewer, đồng thời cung cấp lời giải thích rõ ràng cho từng đánh giá và dashboard tổng hợp cho từng nhà hàng.**

### 5.2. Mục tiêu cụ thể (phân rã từ mục tiêu chung)

| Mã MT | Mục tiêu cụ thể | Đo lường kết quả (KPI) |
|-------|-----------------|------------------------|
| **MT1** | Xây dựng **data pipeline** thu thập + tiền xử lý + gán nhãn dataset F&B tiếng Việt | ~3.000 review có nhãn, κ ≥ 0.70, dataset có documentation rõ ràng |
| **MT2** | **Fine-tune PhoBERT-base** cho binary classification genuine vs fake | F1-macro ≥ 0.83, Accuracy ≥ 0.85 trên test set |
| **MT3** | Thiết kế và triển khai **Layer 1 — Content Module** (PhoBERT + sentiment-star check + aspect + TTR + SimHash) | Unit test coverage ≥ 80%, kiểm thử 100+ case |
| **MT4** | Thiết kế và triển khai **Layer 2 — Behavior Module** (review count + frequency + burst + rating pattern) | Unit test coverage ≥ 80% |
| **MT5** | Thiết kế **Trust Engine** gộp 2 layer → Trust Score + badge + explanation | Mỗi review có explanation ≥ 3 lý do, Trust Score 0–100 |
| **MT6** | Xây dựng **Web Application** 3 trang: `/`, `/restaurant/:slug`, `/analyze` | SPA React hoạt động, UX test OK với ≥ 5 người dùng |
| **MT7** | Thực nghiệm **Ablation Study** chứng minh đóng góp của từng layer | Báo cáo bảng: baseline PhoBERT-only vs +Behavior vs full; tăng ≥ 3% F1 |
| **MT8** | Xây dựng **Case Study thực tế** trên 3–5 quán tại HCM | Phát hiện ≥ 1 cluster suspicious có evidence rõ ràng |

### 5.3. Câu hỏi nghiên cứu (Research Questions)

- **RQ1:** Việc kết hợp PhoBERT (content) với behavioral rules có cải thiện F1-score bao nhiêu so với chỉ dùng PhoBERT trên dữ liệu F&B tiếng Việt?
- **RQ2:** Trong behavioral features (review count, frequency, burst, rating pattern), feature nào đóng góp nhiều nhất vào performance?
- **RQ3:** Cách trình bày XAI (danh sách lý do) có giúp người dùng cuối tin vào Trust Score hơn so với chỉ trả về nhãn không? (Khảo sát UX N=20 người).

---

## 6. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG (UC/ERD)

### 6.1. Phân rã mục tiêu thành chức năng hệ thống (Function Decomposition)

```
ReviewTrust System
├── [F1] Thu thập dữ liệu
│   ├── F1.1 Scrape Google Maps từ URL (Playwright)
│   ├── F1.2 Scrape Foody (BeautifulSoup)
│   └── F1.3 Nhận review nhập tay (demo)
├── [F2] Phân tích nội dung (Content Module)
│   ├── F2.1 PhoBERT genuine probability inference
│   ├── F2.2 Sentiment-star consistency check
│   ├── F2.3 Aspect extraction (rule-based)
│   ├── F2.4 TTR + Length check
│   └── F2.5 SimHash duplicate detection
├── [F3] Phân tích hành vi (Behavior Module)
│   ├── F3.1 Reviewer history check (count)
│   ├── F3.2 Review frequency check
│   ├── F3.3 Burst detection
│   └── F3.4 Rating pattern check
├── [F4] Trust Engine
│   ├── F4.1 Gộp Content + Behavior → Trust Score
│   ├── F4.2 Quyết định badge
│   └── F4.3 Sinh explanation
├── [F5] Hiển thị Dashboard
│   ├── F5.1 Trust Gauge + Void Score
│   ├── F5.2 Adjusted Rating
│   ├── F5.3 Timeline + Burst highlight
│   ├── F5.4 Suspicious Clusters
│   └── F5.5 Review list + breakdown
└── [F6] Quản trị dữ liệu
    ├── F6.1 Lưu Review + Score vào DB
    └── F6.2 Quản lý scrape jobs (async)
```

### 6.2. Sơ đồ Use Case

**Actor chính:**

- **Traveler (Người dùng cuối):** người đọc review, cần đánh giá độ tin cậy trước khi đi ăn.
- **System (hệ thống tự động):** bot scrape + background worker.

```
┌──────────────── ReviewTrust ────────────────┐
│                                              │
│  Traveler ─── (UC1) Phân tích 1 review       │
│       │                                      │
│       ├─── (UC2) Phân tích nhà hàng từ URL   │
│       │         │                            │
│       │         └── «include» (UC7) Scrape  │
│       │                                      │
│       ├─── (UC3) Xem dashboard quán          │
│       │         │                            │
│       │         ├── «include» (UC4) Xem      │
│       │         │         breakdown + XAI    │
│       │         ├── «include» (UC5) Xem      │
│       │         │         suspicious cluster │
│       │         └── «include» (UC6) Xem      │
│       │                   timeline burst     │
│       │                                      │
│       └─── (UC8) Poll trạng thái job scrape  │
│                                              │
│  System  ─── (UC9) Background: chạy scoring  │
│       └─── (UC10) Lưu DB + cache             │
│                                              │
└──────────────────────────────────────────────┘
```

### 6.3. Đặc tả các Use Case chính

#### UC1: Phân tích 1 review (Demo mode)

| Thuộc tính | Chi tiết |
|-----------|---------|
| **Actor** | Traveler |
| **Tiền điều kiện** | Web app đã load, API backend chạy |
| **Luồng chính** | 1. User truy cập `/analyze`<br>2. Nhập review text + số sao (1–5) vào form<br>3. (Tuỳ chọn) nhập `review_count` của reviewer<br>4. Nhấn "Phân tích"<br>5. FE gọi `POST /api/v1/analyze`<br>6. BE chạy Content Module → trả Trust Score + badge + explanation<br>7. FE hiển thị gauge + danh sách lý do |
| **Luồng phụ** | 6a. Không có reviewer_count → chỉ chạy Content → caveat "không có behavior data" |
| **Hậu điều kiện** | Kết quả hiển thị, không lưu DB |

#### UC2: Phân tích nhà hàng từ URL Google Maps

| Thuộc tính | Chi tiết |
|-----------|---------|
| **Actor** | Traveler |
| **Tiền điều kiện** | URL hợp lệ Google Maps |
| **Luồng chính** | 1. User paste URL vào trang chủ<br>2. FE gọi `POST /api/v1/scrape` → nhận 202 + `job_id`<br>3. FE poll `GET /api/v1/scrape/status/{job_id}` mỗi 3s<br>4. Background worker scrape reviews (Playwright)<br>5. Với mỗi review: chạy Content + Behavior → lưu DB<br>6. Worker hoàn tất → status = `success`<br>7. FE redirect `/restaurant/:slug` |
| **Luồng phụ (lỗi)** | 4a. Captcha / rate limit → job status = `failed`, hiện lỗi |
| **Hậu điều kiện** | Dữ liệu quán + reviews + trust_scores đã lưu DB |

#### UC3: Xem dashboard quán

| Thuộc tính | Chi tiết |
|-----------|---------|
| **Actor** | Traveler |
| **Tiền điều kiện** | Quán đã được scrape & scored |
| **Luồng chính** | 1. User truy cập `/restaurant/:slug`<br>2. FE gọi `GET /api/v1/restaurant/{slug}`<br>3. BE trả: info quán + reviews + scores + aggregated stats<br>4. FE render: Trust Gauge tổng, Adjusted Rating, Timeline, Suspicious Cluster, list reviews |

### 6.4. Sơ đồ ERD

```
┌──────────────────────┐
│ restaurants          │
├──────────────────────┤
│ id (PK)              │
│ name                 │
│ slug (UQ)            │
│ google_place_id (UQ) │
│ google_maps_url      │
│ address              │
│ last_scraped_at      │
│ created_at           │
└──────────┬───────────┘
           │ 1
           │
           │ *
┌──────────▼───────────┐                  ┌──────────────────────┐
│ reviews              │                  │ scrape_jobs          │
├──────────────────────┤                  ├──────────────────────┤
│ id (PK)              │          ┌──── *│ id (PK)              │
│ restaurant_id (FK)   │◄─────────┘ 1  ──│ restaurant_id (FK)   │
│ content              │                  │ status               │
│ star_rating          │                  │ error_message        │
│ reviewer_name        │                  │ started_at           │
│ reviewer_review_count│                  │ finished_at          │
│ posted_at            │                  └──────────────────────┘
│ simhash              │
│ source               │   (google_maps / foody / manual)
│ created_at           │
└──────────┬───────────┘
           │ 1
           │
           │ 1
┌──────────▼───────────┐
│ trust_scores         │
├──────────────────────┤
│ id (PK)              │
│ review_id (FK, UQ)   │
│ content_score        │   FLOAT 0–100
│ behavior_score       │   FLOAT 0–100 (nullable nếu demo mode)
│ trust_score          │   FLOAT 0–100
│ void_score           │   FLOAT = 100 − trust_score
│ badge                │   VARCHAR: trusted / caution / suspicious
│ explanation          │   JSONB: list of reasons
│ model_version        │   VARCHAR
│ content_only         │   BOOLEAN
│ created_at           │
└──────────────────────┘
```

**Ràng buộc chính:**
- `restaurants.slug` UNIQUE → URL thân thiện.
- `reviews.simhash` index → tăng tốc duplicate check.
- `trust_scores.review_id` UNIQUE → mỗi review 1 score.
- `scrape_jobs` độc lập với `reviews` vì 1 job có thể scrape nhiều review.

---

## 7. PHƯƠNG PHÁP ĐỀ XUẤT — KIẾN TRÚC 2 LAYER

### 7.1. Tổng quan

Kế thừa triết lý fuse sequential+nonsequential của ConvRoBERTa, ReviewTrust dùng kiến trúc **2-layer** đơn giản hoá phù hợp quy mô đồ án:

```
┌──────────────────────────────────────────────────────┐
│                  INPUT: 1 review                     │
│  { content, star, reviewer_name, review_count, ...} │
└────────┬─────────────────────────────┬──────────────┘
         │                             │
         ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│  LAYER 1         │          │  LAYER 2         │
│  Content Module  │          │  Behavior Module │
│  (60% trọng số)  │          │  (40% trọng số)  │
│                  │          │                  │
│ • PhoBERT prob   │          │ • Review count   │
│ • Sentiment-star │          │ • Frequency (1h) │
│ • Aspect         │          │ • Burst (day)    │
│ • TTR + Length   │          │ • Rating pattern │
│ • SimHash dup    │          │                  │
└────────┬─────────┘          └────────┬─────────┘
         │ content_score                │ behavior_score
         │ (0–100)                      │ (0–100)
         └──────────┬───────────────────┘
                    ▼
         ┌──────────────────┐
         │   TRUST ENGINE   │
         │                  │
         │ Trust = 0.6 × C  │
         │       + 0.4 × B  │
         │                  │
         │ Badge decision   │
         │ Explainer        │
         └────────┬─────────┘
                  ▼
         { trust_score, void_score, badge,
           explanation[], breakdown }
```

### 7.2. Layer 1 — Content Module (chi tiết scoring)

| Yếu tố | Điều kiện | Điểm |
|--------|-----------|------|
| Base | `content_score = PhoBERT genuine_prob × 100` | (0–100) |
| Sentiment-star mâu thuẫn | Text khen + star 1–2, hoặc ngược | −25 |
| Aspect count | ≥ 3 | +15 |
| Aspect count | = 2 | +10 |
| Aspect count | = 0 | −15 |
| TTR (Type-Token Ratio) | < 0.4 (lặp từ nhiều) | −10 |
| TTR | > 0.7 + text dài | +5 |
| Length | < 10 từ | −30 |
| Length | 10–19 từ | −20 |
| Length | ≥ 50 từ + có aspect | +5 |
| SimHash similarity | > 90% với review khác | −40 |
| SimHash similarity | 80–90% | −30 |

Clamp về `[0, 100]`.

### 7.3. Layer 2 — Behavior Module

| Yếu tố | Điều kiện | Điểm |
|--------|-----------|------|
| Review count | < 3 | −15 |
| Review count | 3–4 | −10 |
| Review count | ≥ 10 | +5 |
| Frequency | ≥ 6 review trong 1h | −30 |
| Burst | Reviewer thuộc cụm ≥ 15 tài khoản mới cùng ngày | −25 |
| Rating pattern | Liên tiếp cùng sao (chỉ 5★ hoặc chỉ 1★) | −15 |

### 7.4. Trust Engine

```
Trust Score = 0.60 × Content Score + 0.40 × Behavior Score
Void Score  = 100 − Trust Score

Badge:
  ≥ 75   → "Đáng tin cậy" (trusted, #22c55e)
  50–74  → "Cần thận trọng" (caution, #eab308)
  < 50   → "Nghi ngờ" (suspicious, #ef4444)
```

**Nếu demo mode** (không có reviewer metadata): Trust = Content, gắn cờ `content_only = true`.

### 7.5. So sánh với các phương pháp baseline (dự kiến khi báo cáo)

| Baseline | Thành phần | F1 dự kiến |
|----------|------------|-----------|
| B1: PhoBERT-only | Chỉ PhoBERT | 0.80 |
| B2: Rules-only | Chỉ rule Content + Behavior | 0.72 |
| B3: PhoBERT + Content rules | Chỉ Layer 1 | 0.82 |
| **B4: Full ReviewTrust** | **Layer 1 + Layer 2 + Trust Engine** | **0.85** (mục tiêu) |
| B5 (tham chiếu): ConvRoBERTa (tiếng Anh) | Full paper | 0.92 |

---

## 8. CÔNG NGHỆ SỬ DỤNG

| Tầng | Công nghệ | Lý do chọn |
|------|-----------|-----------|
| **ML / NLP** | PyTorch 2.x, HuggingFace Transformers, PhoBERT-base | PhoBERT là SOTA tiếng Việt (Nguyen & Nguyen 2020) |
| **NLP utilities** | underthesea / pyvi (word-seg), datasketch (SimHash) | Chuẩn cho PhoBERT input |
| **Backend** | FastAPI (Python 3.11+), SQLAlchemy 2.x async + asyncpg | Async cao, type-safe, Swagger auto-gen |
| **Scraping** | Playwright 1.x (Chromium headless), BeautifulSoup4 | Playwright xử lý DOM động (Google Maps SPA) |
| **Database** | PostgreSQL 16 | JSONB cho `explanation`, hỗ trợ full-text, ổn định |
| **Migration** | Alembic | Version DB schema |
| **Frontend** | React 18 + Vite + TailwindCSS + Recharts | Dev nhanh, component-based, chart đẹp |
| **Deploy** | Docker Compose → Railway/Render free tier | Reproducible, chi phí 0đ |
| **Testing** | pytest (backend), Vitest (frontend) | Chuẩn |

---

## 9. KẾ HOẠCH THỰC HIỆN (12 TUẦN)

| Tuần | Công việc | Deliverable |
|------|-----------|-------------|
| **1** | Hoàn tất đề cương + khảo sát 5 paper + setup repo + env | Proposal + Notes khảo sát + Repo Git |
| **2** | Scrape Google Maps ~2.000 review; Foody ~800 review; tiền xử lý | Raw dataset CSV/JSONL |
| **3** | Gán nhãn tầng 1 (heuristics) + tầng 2 (LLM-assisted) | Dataset labeled v0.5 |
| **4** | Gán nhãn tầng 3 (manual 500 gold + 500 arbitration); tính Cohen's Kappa | Dataset final + κ report |
| **5** | Fine-tune PhoBERT (3–5 epochs) + hyper-param tuning | `phobert_voidrv.pt` + metrics |
| **6** | Triển khai Content Module + Behavior Module + unit tests | `services/*.py` + tests coverage 80% |
| **7** | Triển khai Trust Engine + XAI Explainer + integration tests | API `/analyze` hoạt động |
| **8** | Scraper Google Maps + Background worker + scrape_jobs flow | API `/scrape` + `/scrape/status` |
| **9** | Frontend 3 trang (Home + Analyze + Restaurant Dashboard) | SPA React hoạt động end-to-end |
| **10** | Ablation study + Case study 3–5 quán thật + viết chương 4 báo cáo | Notebook + bảng metrics + case study |
| **11** | Khảo sát UX N=20 + XAI user test + hoàn thiện UI | UX report |
| **12** | Deploy Docker, viết báo cáo quyển, slide demo | URL public + .docx + .pptx |

---

## 10. DỰ KIẾN RỦI RO VÀ GIẢI PHÁP

| Rủi ro | Mức độ | Giải pháp phòng ngừa |
|--------|--------|----------------------|
| Google Maps chặn scrape (CAPTCHA, rate-limit) | Cao | Random User-Agent, delay 2–5s, giới hạn ≤ 200 req/giờ, có fallback dataset thủ công |
| Dataset mất cân bằng nhãn nặng | Cao | Augment fake class bằng LLM (Luo 2026 gợi ý); dùng `class_weight` + focal loss |
| κ gán nhãn < 0.70 → nhãn không tin cậy | Trung bình | Bổ sung vòng arbitration thứ 2; rà guideline chặt hơn |
| F1 PhoBERT < 0.80 sau fine-tune | Trung bình | Thử PhoBERT-large; tăng dữ liệu bằng back-translation; thử ConvPhoBERT adapt từ ConvRoBERTa |
| RTX 3060 12GB không đủ train PhoBERT-large | Trung bình | Dùng gradient accumulation; batch_size=8; hoặc Colab Pro |
| PhoBERT model size ~540MB khó deploy free tier | Thấp | Export ONNX quantized INT8 (giảm ~75%); hoặc dùng async inference queue |
| Foody.vn đổi layout HTML | Thấp | Viết test e2e scraper; có fallback chỉ dùng Google Maps |
| Tranh chấp pháp lý khi scrape | Thấp | Chỉ scrape cho mục đích học thuật, không public raw data, ẩn danh reviewer_name trước khi công bố |

---

## 11. CẤU TRÚC QUYỂN BÁO CÁO DỰ KIẾN

- **MỞ ĐẦU:** Tính cấp thiết, mục tiêu, phạm vi, phương pháp, ý nghĩa.
- **CHƯƠNG 1 — TỔNG QUAN:** Bài toán FRD, thực trạng, khảo sát nghiên cứu liên quan (5 paper đã khảo sát), khoảng trống và hướng kế thừa.
- **CHƯƠNG 2 — CƠ SỞ LÝ THUYẾT:** PhoBERT, Transformer, SimHash, TTR, Aspect-based Sentiment, Behavioral Features, XAI.
- **CHƯƠNG 3 — PHÂN TÍCH & THIẾT KẾ HỆ THỐNG:** UC diagram, ERD, API specs, kiến trúc 2-layer, luồng xử lý.
- **CHƯƠNG 4 — CÀI ĐẶT & THỰC NGHIỆM:** Fine-tune PhoBERT, ablation study, case study thật, UX test, so sánh baseline.
- **CHƯƠNG 5 — GIAO DIỆN & DEMO:** Screenshots web app, demo video, hướng dẫn sử dụng.
- **KẾT LUẬN & HƯỚNG PHÁT TRIỂN:** đóng góp đạt được, hạn chế, hướng mở rộng (Foody cross-platform, LLM-generated detection, stylometry).
- **TÀI LIỆU THAM KHẢO.**

---

## 12. TÀI LIỆU THAM KHẢO

### Quốc tế (theo thầy gửi)

[1] Luo, J., Nan, G., & Li, D. (2026). *AI-generated fake review detection.* **Decision Support Systems.** Elsevier.

[2] Zhang, Z., Ngai, E. W. T., Xia, S., & Wu, Z. (2025). *Enhancing fake review detection: A robust and adaptive approach for data streams.* **Knowledge-Based Systems.** Elsevier.

[3] Qi, C., Li, X., Yang, X., & Li, Z. (2025). *A review of fake news detection based on transfer learning.* **Information Fusion.** Elsevier.

[4] Xu, T., & Huo, Y. (2026). *Interpretable fake review detection based on multimodal information and human–computer collaboration.* **Applied Soft Computing.** Elsevier.

[5] Mewada, A., & Dewang, R. K. (2026). *ConvRoBERTa: Detecting Fake Reviews by Fusing Sequential and Weighted Nonsequential Features.* **IEEE Transactions on Artificial Intelligence**, 7(3), 1301–1314. [Phương pháp nền kế thừa chính]

### Các nghiên cứu tiếng Việt

[6] Dinh, C. V., Luu, S. T., et al. (2022). *Detecting Spam Reviews on Vietnamese E-commerce Websites.* arXiv:2207.14636.

[7] Dinh, C. V., & Luu, S. T. (2024). *Metadata Integration for Spam Reviews Detection on Vietnamese E-commerce Websites.* arXiv:2405.13292.

[8] Nguyen, D. Q., & Nguyen, A. T. (2020). *PhoBERT: Pre-trained language models for Vietnamese.* Findings of EMNLP 2020.

### Các công trình nền tảng

[9] Jindal, N., & Liu, B. (2008). *Opinion Spam and Analysis.* WSDM.

[10] Ott, M., Choi, Y., Cardie, C., & Hancock, J. T. (2011). *Finding Deceptive Opinion Spam by Any Stretch of the Imagination.* ACL.

[11] Mukherjee, A., Venkataraman, V., Liu, B., & Glance, N. (2013). *What Yelp Fake Review Filter Might Be Doing?* ICWSM.

[12] Rayana, S., & Akoglu, L. (2015). *Collective Opinion Spam Detection.* KDD.

[13] Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.* NAACL-HLT.

### Tài liệu kỹ thuật

[14] FastAPI documentation — https://fastapi.tiangolo.com/
[15] HuggingFace Transformers documentation — https://huggingface.co/docs/transformers
[16] Playwright for Python documentation — https://playwright.dev/python/
[17] PhoBERT GitHub (VinAIResearch) — https://github.com/VinAIResearch/PhoBERT
