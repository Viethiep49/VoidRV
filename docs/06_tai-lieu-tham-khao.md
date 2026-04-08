# VoidRV — Tài liệu tham khảo

---

## 1. Papers chính

### Fake Review Detection — Nền tảng

1. **Jindal, N., & Liu, B. (2008).** "Opinion Spam and Analysis." *WSDM 2008.*
   - Paper gốc fake review detection

2. **Ott, M., Choi, Y., Cardie, C., & Hancock, J.T. (2011).** "Finding Deceptive Opinion Spam by Any Stretch of the Imagination." *ACL 2011.*
   - Methodology tạo dataset fake review — VoidRV tham khảo: dùng GPT-4o thay Mechanical Turk

3. **Mukherjee, A., Venkataraman, V., Liu, B., & Glance, N. (2013).** "What Yelp Fake Review Filter Might Be Doing?" *ICWSM 2013.*
   - Behavioral signals: account age, review frequency, rating pattern

4. **Rayana, S., & Akoglu, L. (2015).** "Collective Opinion Spam Detection: Bridging Review Networks and Metadata." *KDD 2015.*
   - Content + behavior/metadata — cùng hướng VoidRV

### Fake Review Detection — Tiếng Việt

5. **Co Van Dinh, Son T. Luu, Anh Gia-Tuan Nguyen (2022).** "Detecting Spam Reviews on Vietnamese E-commerce Websites." *arXiv:2207.14636.*
   - Dataset ViSpamDetection — VoidRV dùng train

6. **Co Van Dinh, Son T. Luu (2024).** "Metadata Integration for Spam Reviews Detection on Vietnamese E-commerce Websites." *arXiv:2405.13292.*
   - Dataset ViSpamReviews — VoidRV dùng train

### AI-Generated Fake Reviews

7. **Gambetti, A., & Han, Q. (2024).** "AiGen-FoodReview: A Multimodal Dataset of Machine-Generated Restaurant Reviews." *ICWSM 2024. arXiv:2401.08825.*
   - Tham khảo methodology generate fake reviews domain nhà hàng

### NLP tiếng Việt

8. **Nguyen, D.Q., & Nguyen, A.T. (2020).** "PhoBERT: Pre-trained language models for Vietnamese." *Findings of EMNLP 2020.*
   - Model NLP chính VoidRV sử dụng

9. **Devlin, J., Chang, M.W., Lee, K., & Toutanova, K. (2019).** "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." *NAACL 2019.*
   - Kiến trúc nền tảng PhoBERT

### Stylometry / Authorship Analysis

10. **Koppel, M., & Schler, J. (2004).** "Authorship verification as a one-class classification problem." *ICML 2004.*
    - Nền tảng stylometry — VoidRV áp dụng cho reviewer identity

11. **Stamatatos, E. (2009).** "A Survey of Modern Authorship Attribution Methods." *JASIST.*
    - Survey toàn diện — character n-grams, TF-IDF approach

### Cross-Platform / Metadata-aware

12. **[2024]** "A metadata-aware detection model for fake restaurant reviews based on multimodal fusion." *Neural Computing and Applications, Springer.*
    - Cùng bài toán — dẫn để so sánh

---

## 2. Datasets sử dụng

| Dataset | Link | Domain | Cách dùng |
|---------|------|--------|-----------|
| **ViSpamReviews** | `huggingface.co/datasets/visolex/ViSpamReviews` | E-commerce VN | Train |
| **ViSpamDetection v2** | `huggingface.co/datasets/clapAI/ViSpamDetectionv2` | E-commerce VN | Train |
| **vi-ntc-scv** | `huggingface.co/datasets/thainq107/vi-ntc-scv` | Ăn uống VN | Convert → genuine |
| **sonlam1102/vispamdetection** | `huggingface.co/datasets/sonlam1102/vispamdetection` | E-commerce VN | Cần agree terms |
| **Google Maps scrape** | Tự scrape (Playwright) | Nhà hàng VN | Domain adaptation |
| **Foody.vn scrape** | Tự scrape (httpx+BS4) | Nhà hàng VN | Cross-platform + genuine |
| **GPT-4o generated** | Tự tạo | Nhà hàng VN | Augment fake class |

---

## 3. Thư viện & Framework

| Thư viện | Mục đích |
|----------|----------|
| FastAPI | Backend REST API |
| PyTorch 2.x | ML framework |
| HuggingFace Transformers | Load/fine-tune PhoBERT |
| HuggingFace Datasets | Tải dataset |
| scikit-learn | TF-IDF stylometry + cosine similarity + chi-square |
| React 18 | Frontend SPA |
| Vite 5 | Build tool |
| TailwindCSS 3 | CSS |
| Recharts | Charts (timeline, pie, bar) |
| SQLAlchemy 2.x | ORM async |
| PostgreSQL 16 | Database |
| Playwright | Google Maps scraping |
| playwright-stealth | Bypass bot detection |
| httpx | Async HTTP (Foody scraper) |
| BeautifulSoup4 | HTML parser (Foody) |
| datasketch | SimHash duplicate detection |
| Docker Compose | Deploy |
