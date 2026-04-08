"""Generate ReviewTrust Proposal Word Document"""
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import os

doc = Document()

# ============================================================
# Page setup
# ============================================================
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3)
    section.right_margin = Cm(2)

style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(13)
style.paragraph_format.line_spacing = 1.5

# ============================================================
# Helper functions
# ============================================================
def add_heading_custom(text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = 'Times New Roman'
        run.font.color.rgb = RGBColor(0, 0, 0)
    return h

def add_paragraph(text, bold=False, italic=False, align=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13)
    run.bold = bold
    run.italic = italic
    if align:
        p.alignment = align
    return p

def add_table(headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Light Grid Accent 1'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
    # Rows
    for row_data in rows:
        row = table.add_row()
        for i, val in enumerate(row_data):
            cell = row.cells[i]
            cell.text = str(val)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(12)
    doc.add_paragraph()
    return table

# ============================================================
# TRANG BÌA
# ============================================================
for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('BỘ GIÁO DỤC VÀ ĐÀO TẠO')
run.font.name = 'Times New Roman'
run.font.size = Pt(14)
run.bold = True

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('TRƯỜNG ĐẠI HỌC CÔNG NGHỆ TP.HCM (HUTECH)')
run.font.name = 'Times New Roman'
run.font.size = Pt(14)
run.bold = True

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('KHOA CÔNG NGHỆ THÔNG TIN')
run.font.name = 'Times New Roman'
run.font.size = Pt(14)
run.bold = True

for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('ĐỀ CƯƠNG ĐỒ ÁN CHUYÊN NGÀNH')
run.font.name = 'Times New Roman'
run.font.size = Pt(16)
run.bold = True

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('REVIEWTRUST — HỆ THỐNG ĐÁNH GIÁ\nĐỘ TIN CẬY REVIEW NHÀ HÀNG TẠI VIỆT NAM')
run.font.name = 'Times New Roman'
run.font.size = Pt(18)
run.bold = True
run.font.color.rgb = RGBColor(0, 51, 102)

for _ in range(4):
    doc.add_paragraph()

info_lines = [
    ('Chuyên ngành:', 'Hệ thống Thông tin Ứng dụng'),
    ('Sinh viên thực hiện:', 'Trương Viết Hiệp'),
    ('Giảng viên hướng dẫn:', '...............................................'),
]
for label, value in info_lines:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f'{label} ')
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13)
    run.bold = True
    run = p.add_run(value)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13)

for _ in range(3):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('TP. Hồ Chí Minh, 2026')
run.font.name = 'Times New Roman'
run.font.size = Pt(13)
run.italic = True

doc.add_page_break()

# ============================================================
# MỤC LỤC
# ============================================================
add_heading_custom('MỤC LỤC', level=1)
toc_items = [
    '1. Giới thiệu đề tài',
    '   1.1. Đặt vấn đề',
    '   1.2. Mục tiêu',
    '   1.3. Phạm vi',
    '2. Cơ sở lý thuyết',
    '   2.1. Fake Review Detection',
    '   2.2. PhoBERT',
    '   2.3. Behavioral Analysis',
    '3. Phân tích và thiết kế hệ thống',
    '   3.1. Kiến trúc tổng quan',
    '   3.2. Luồng xử lý',
    '   3.3. Cơ sở dữ liệu',
    '4. Scoring Logic',
    '   4.1. Content Score',
    '   4.2. Behavior Score',
    '   4.3. Trust Score',
    '5. Data Pipeline',
    '   5.1. Thu thập dữ liệu',
    '   5.2. Gán nhãn',
    '   5.3. Fine-tune PhoBERT',
    '6. Công nghệ sử dụng',
    '7. Kế hoạch thực hiện',
    '8. Tài liệu tham khảo',
]
for item in toc_items:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(2)
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

doc.add_page_break()

# ============================================================
# CHƯƠNG 1: GIỚI THIỆU ĐỀ TÀI
# ============================================================
add_heading_custom('CHƯƠNG 1: GIỚI THIỆU ĐỀ TÀI', level=1)

add_heading_custom('1.1. Đặt vấn đề', level=2)
add_paragraph(
    'Trong bối cảnh thương mại điện tử và dịch vụ ẩm thực phát triển mạnh tại Việt Nam, '
    'các nền tảng đánh giá như Google Maps, Foody, TripAdvisor đóng vai trò quan trọng trong '
    'việc giúp người tiêu dùng lựa chọn nhà hàng. Tuy nhiên, vấn đề review giả (fake review) '
    'ngày càng trở nên nghiêm trọng:'
)
bullets = [
    'Review farm: các tổ chức thuê người viết review 5 sao hàng loạt cho nhà hàng',
    'Tài khoản ảo: bot tự động tạo tài khoản và viết review theo kịch bản',
    'Review cạnh tranh không lành mạnh: đối thủ viết review 1 sao để hạ uy tín',
    'Review generic: nội dung chung chung, không có giá trị tham khảo ("Ngon lắm!", "Tuyệt vời!")',
]
for b in bullets:
    p = doc.add_paragraph(b, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

add_paragraph(
    'Theo nghiên cứu của Jindal & Liu (2008), khoảng 30% review trên các nền tảng thương mại điện tử '
    'có dấu hiệu spam hoặc fake. Các nền tảng hiện tại tại Việt Nam chưa cung cấp công cụ nào '
    'giúp người dùng đánh giá độ tin cậy của từng review cụ thể.'
)

add_heading_custom('1.2. Mục tiêu', level=2)
add_paragraph('Đồ án hướng đến xây dựng hệ thống ReviewTrust với các mục tiêu cụ thể:', bold=False)
targets = [
    'Xây dựng hệ thống web phân tích và đánh giá độ tin cậy của review nhà hàng tại Việt Nam',
    'Ứng dụng mô hình PhoBERT (pretrained cho tiếng Việt) để phát hiện review fake/spam',
    'Kết hợp phân tích nội dung (NLP) và phân tích hành vi (behavioral) để tạo Trust Score đa chiều',
    'Cung cấp giải thích minh bạch cho mỗi đánh giá, giúp người dùng hiểu tại sao review đáng tin hoặc không',
    'Thu thập và xây dựng bộ dataset review tiếng Việt phục vụ đánh giá hệ thống',
]
for t in targets:
    p = doc.add_paragraph(t, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

add_heading_custom('1.3. Phạm vi', level=2)
add_paragraph('Phạm vi thực hiện:', bold=True)
scope_in = [
    'Web application (React + FastAPI) với 2 trang: phân tích review và dashboard quán',
    'Fine-tune PhoBERT cho bài toán binary classification (genuine vs fake review)',
    'Rule-based behavior scoring dựa trên metadata người viết review',
    'Scrape dữ liệu từ Google Maps và Foody để xây dựng dataset và demo',
    'Copy-paste detection bằng SimHash',
]
for s in scope_in:
    p = doc.add_paragraph(s, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

add_paragraph('Ngoài phạm vi (KHÔNG thực hiện):', bold=True)
scope_out = [
    'Không xử lý ảnh, GPS, Vision Transformer',
    'Không eKYC, xác thực danh tính',
    'Không browser extension',
    'Không mobile application',
    'Không train model từ đầu (chỉ fine-tune pretrained)',
]
for s in scope_out:
    p = doc.add_paragraph(s, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

doc.add_page_break()

# ============================================================
# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT
# ============================================================
add_heading_custom('CHƯƠNG 2: CƠ SỞ LÝ THUYẾT', level=1)

add_heading_custom('2.1. Fake Review Detection', level=2)
add_paragraph(
    'Fake review detection là lĩnh vực nghiên cứu nhằm phát hiện các đánh giá không trung thực '
    'trên các nền tảng thương mại điện tử. Theo phân loại của Jindal & Liu (2008), opinion spam '
    'được chia thành 3 loại:'
)
spam_types = [
    'Type 1 — Untruthful opinions: review có nội dung sai sự thật, viết nhằm đánh lừa người đọc',
    'Type 2 — Reviews on brands only: review không nói về sản phẩm/dịch vụ cụ thể',
    'Type 3 — Non-reviews: nội dung không phải review (quảng cáo, câu hỏi, spam)',
]
for s in spam_types:
    p = doc.add_paragraph(s, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

add_paragraph(
    'Các phương pháp phát hiện fake review được chia thành 2 hướng chính: '
    '(1) Content-based — phân tích nội dung text bằng NLP, và '
    '(2) Behavior-based — phân tích hành vi của reviewer (Mukherjee et al., 2013). '
    'ReviewTrust kết hợp cả hai hướng này.'
)

add_heading_custom('2.2. PhoBERT — Pre-trained Language Model cho tiếng Việt', level=2)
add_paragraph(
    'PhoBERT (Nguyen & Nguyen, 2020) là mô hình ngôn ngữ pretrained dựa trên kiến trúc BERT '
    '(Devlin et al., 2019), được huấn luyện trên 20GB dữ liệu tiếng Việt từ Wikipedia và các '
    'nguồn báo chí Việt Nam. PhoBERT đạt state-of-the-art trên nhiều bài toán NLP tiếng Việt '
    'bao gồm Part-of-Speech tagging, Named Entity Recognition, và Dependency Parsing.'
)
add_paragraph(
    'Trong ReviewTrust, PhoBERT được sử dụng cho 2 task:'
)
phobert_tasks = [
    'Binary classification: phân loại review genuine vs fake',
    'Sentiment analysis: xác định sentiment (tích cực/tiêu cực) để so sánh với star rating',
]
for t in phobert_tasks:
    p = doc.add_paragraph(t, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

add_paragraph(
    'PhoBERT-base có 135 triệu tham số, sử dụng tokenizer RoBERTa với vocab size 64,000 tokens. '
    'Fine-tune PhoBERT cho text classification chỉ cần thêm 1 classification head '
    '(linear layer) trên [CLS] token output.'
)

add_heading_custom('2.3. Behavioral Analysis', level=2)
add_paragraph(
    'Mukherjee et al. (2013) chỉ ra rằng hành vi của reviewer là tín hiệu mạnh để phát hiện '
    'fake review. Các tín hiệu behavioral bao gồm:'
)
add_table(
    ['Tín hiệu', 'Ý nghĩa'],
    [
        ['Account age', 'Tài khoản mới tạo có xác suất cao là tài khoản ảo'],
        ['Review count', 'Tài khoản ít review → chưa đủ lịch sử đánh giá'],
        ['Review diversity', 'Chỉ review 1 quán → khả năng cao là thuê viết'],
        ['Review frequency', 'Nhiều review trong thời gian ngắn → bot/spam'],
        ['Rating pattern', 'Chỉ cho 5 sao hoặc 1 sao → thiên lệch'],
    ]
)
add_paragraph(
    'ReviewTrust sử dụng các tín hiệu trên dưới dạng rule-based scoring, '
    'với mỗi vi phạm sẽ trừ điểm từ base score 100.'
)

doc.add_page_break()

# ============================================================
# CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG
# ============================================================
add_heading_custom('CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG', level=1)

add_heading_custom('3.1. Kiến trúc tổng quan', level=2)
add_paragraph(
    'Hệ thống ReviewTrust được thiết kế theo mô hình Client-Server, '
    'gồm 3 tầng chính:'
)
add_table(
    ['Tầng', 'Công nghệ', 'Chức năng'],
    [
        ['Frontend', 'React + Vite + TailwindCSS', 'Giao diện web 2 trang: phân tích và dashboard'],
        ['Backend', 'FastAPI (Python)', 'REST API, scoring engine, ML inference, scraper'],
        ['Database', 'PostgreSQL', 'Lưu trữ reviews, trust scores, thông tin quán'],
    ]
)

add_paragraph(
    'Backend bao gồm 3 module chính xử lý logic:', bold=True
)
modules = [
    'ContentModule: Phân tích nội dung review bằng PhoBERT + rule-based. Trả lời câu hỏi "Nội dung review này có đáng tin không?"',
    'BehaviorModule: Đánh giá hành vi reviewer bằng rule-based. Trả lời câu hỏi "Người viết review này có đáng tin không?"',
    'TrustScoreEngine: Gộp kết quả từ 2 module, tính Trust Score, xác định badge, tạo explanation.',
]
for m in modules:
    p = doc.add_paragraph(m, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

add_heading_custom('3.2. Luồng xử lý', level=2)
add_paragraph('Luồng xử lý chính khi người dùng phân tích 1 review:', bold=True)
flow_steps = [
    'Bước 1: Người dùng nhập review text, star rating, và thông tin reviewer trên giao diện web',
    'Bước 2: Frontend gửi POST request đến /api/v1/analyze',
    'Bước 3: ContentModule phân tích nội dung — PhoBERT inference cho genuine probability, kiểm tra sentiment-star consistency, specificity, length, duplicate',
    'Bước 4: BehaviorModule phân tích metadata — account age, review count, diversity, frequency, rating pattern',
    'Bước 5: TrustScoreEngine tính Trust Score = 60% Content + 40% Behavior, xác định badge, tạo danh sách explanation',
    'Bước 6: Kết quả được lưu vào database và trả về frontend',
    'Bước 7: Frontend hiển thị Trust Score dạng gauge, breakdown chi tiết, và danh sách giải thích',
]
for i, step in enumerate(flow_steps):
    p = doc.add_paragraph(step, style='List Bullet')
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

add_heading_custom('3.3. Cơ sở dữ liệu', level=2)
add_paragraph('Hệ thống sử dụng PostgreSQL với 3 bảng chính:')

add_paragraph('Bảng restaurants:', bold=True)
add_table(
    ['Column', 'Type', 'Ghi chú'],
    [
        ['id', 'SERIAL PK', 'Khóa chính'],
        ['name', 'VARCHAR(255)', 'Tên quán'],
        ['address', 'TEXT', 'Địa chỉ'],
        ['google_place_id', 'VARCHAR(100) UNIQUE', 'ID Google Maps'],
        ['created_at', 'TIMESTAMP', 'Thời gian tạo'],
    ]
)

add_paragraph('Bảng reviews:', bold=True)
add_table(
    ['Column', 'Type', 'Ghi chú'],
    [
        ['id', 'SERIAL PK', 'Khóa chính'],
        ['restaurant_id', 'FK → restaurants.id', 'Liên kết quán'],
        ['content', 'TEXT', 'Nội dung review'],
        ['star_rating', 'SMALLINT', '1–5 sao'],
        ['reviewer_metadata', 'JSONB', 'Thông tin reviewer'],
        ['source', 'VARCHAR(50)', 'Nguồn: google_maps, foody, manual'],
        ['created_at', 'TIMESTAMP', 'Thời gian tạo'],
    ]
)

add_paragraph('Bảng trust_scores:', bold=True)
add_table(
    ['Column', 'Type', 'Ghi chú'],
    [
        ['id', 'SERIAL PK', 'Khóa chính'],
        ['review_id', 'FK → reviews.id UNIQUE', 'Mỗi review 1 score'],
        ['content_score', 'FLOAT', 'Điểm nội dung (0–100)'],
        ['behavior_score', 'FLOAT', 'Điểm hành vi (0–100)'],
        ['trust_score', 'FLOAT', 'Điểm tổng (0–100)'],
        ['badge', 'VARCHAR(20)', 'trusted / caution / suspicious'],
        ['explanation', 'JSONB', 'Mảng các lý do giải thích'],
        ['model_version', 'VARCHAR(50)', 'Phiên bản model'],
        ['created_at', 'TIMESTAMP', 'Thời gian tạo'],
    ]
)

doc.add_page_break()

# ============================================================
# CHƯƠNG 4: SCORING LOGIC
# ============================================================
add_heading_custom('CHƯƠNG 4: SCORING LOGIC', level=1)

add_heading_custom('4.1. Content Score (0–100)', level=2)
add_paragraph(
    'Content Score đánh giá chất lượng và độ tin cậy của nội dung review. '
    'Điểm được tính từ PhoBERT base score, sau đó điều chỉnh bằng các rule:'
)
add_table(
    ['Yếu tố', 'Điều kiện', 'Điểm'],
    [
        ['PhoBERT genuine probability', 'Base score = prob × 100', 'Nền tảng'],
        ['Sentiment mâu thuẫn star', 'Text khen + star 1–2, hoặc ngược lại', '-25'],
        ['Không có chi tiết cụ thể', 'Không đề cập món, giá, tên', '-15'],
        ['Có chi tiết cụ thể', 'Đề cập ≥ 2 loại chi tiết', '+10'],
        ['Review quá ngắn', '< 10 từ', '-30'],
        ['Review ngắn', '10–19 từ', '-20'],
        ['Review dài + chi tiết', '≥ 50 từ + có specificity', '+5'],
        ['Trùng lặp > 90%', 'SimHash similarity với review trong DB', '-40'],
        ['Trùng lặp 80–90%', 'SimHash similarity', '-30'],
    ]
)

add_heading_custom('4.2. Behavior Score (0–100)', level=2)
add_paragraph(
    'Behavior Score đánh giá độ tin cậy của người viết review. '
    'Bắt đầu từ 100 điểm, trừ dần theo các vi phạm:'
)
add_table(
    ['Yếu tố', 'Điều kiện', 'Penalty'],
    [
        ['Tài khoản rất mới', '< 7 ngày', '-30'],
        ['Tài khoản mới', '7–89 ngày', '-10'],
        ['Rất ít review', 'Tổng < 3', '-15'],
        ['Ít review', 'Tổng 3–4', '-10'],
        ['Chỉ review 1 quán', 'unique_restaurants = 1', '-20'],
        ['Ít đa dạng', '2–3 quán', '-5'],
        ['Spam tốc độ cao', '> 5 reviews/giờ', '-50'],
        ['Tần suất cao', '> 3 reviews/giờ', '-40'],
        ['Rating thiên lệch', '100% cho 5★ hoặc 1★', '-15'],
    ]
)

add_heading_custom('4.3. Trust Score', level=2)
add_paragraph('Công thức tổng hợp:', bold=True)
add_paragraph('Trust Score = 0.6 × Content Score + 0.4 × Behavior Score')
add_paragraph(
    'Trọng số 60-40 phản ánh việc nội dung review quan trọng hơn metadata người viết. '
    'Trọng số này có thể điều chỉnh dựa trên kết quả thực nghiệm.'
)
add_paragraph('Phân loại badge:', bold=True)
add_table(
    ['Trust Score', 'Badge', 'Màu', 'Ý nghĩa'],
    [
        ['≥ 75', 'Đáng tin cậy', 'Xanh lá', 'Nội dung cụ thể, reviewer có lịch sử tốt'],
        ['50–74', 'Cần thận trọng', 'Vàng', 'Có dấu hiệu đáng ngờ, cần xem xét thêm'],
        ['< 50', 'Nghi ngờ', 'Đỏ', 'Nhiều dấu hiệu fake/spam'],
    ]
)

doc.add_page_break()

# ============================================================
# CHƯƠNG 5: DATA PIPELINE
# ============================================================
add_heading_custom('CHƯƠNG 5: DATA PIPELINE', level=1)

add_heading_custom('5.1. Thu thập dữ liệu', level=2)
add_table(
    ['Nguồn', 'Phương pháp', 'Số lượng dự kiến', 'Mục đích'],
    [
        ['Google Maps', 'Playwright scraper', '1500–2000 reviews', 'Dataset chính'],
        ['Foody.vn', 'BeautifulSoup scraper', '500–1000 reviews', 'Bổ sung data tiếng Việt'],
        ['GPT-generated', 'Prompt GPT tạo fake reviews', '500 reviews', 'Augment fake class'],
        ['Yelp Dataset', 'Kaggle (có sẵn)', 'Tham khảo', 'Benchmark methodology'],
    ]
)
add_paragraph(
    'Tổng dataset dự kiến: 2000–3000 reviews từ 20–30 quán ăn phổ biến tại Đà Nẵng và TP.HCM.'
)

add_heading_custom('5.2. Gán nhãn (Labeling)', level=2)
add_paragraph('Tiêu chí gán nhãn:', bold=True)
add_table(
    ['Nhãn', 'Tiêu chí', 'Ví dụ'],
    [
        ['Genuine (1)', 'Có chi tiết cụ thể, ngôn ngữ tự nhiên, có cả ưu và nhược',
         '"Phở bò tái nạm ngon, nước dùng đậm vị, giá 55k hơi cao so với khu vực"'],
        ['Fake (0)', 'Generic, quá ngắn, copy-paste, khen/chê thái quá không lý do',
         '"Quán ngon lắm!!!" hoặc "Dở lắm, không bao giờ quay lại"'],
    ]
)
add_paragraph(
    'Dự kiến gán nhãn thủ công 500–1000 reviews bằng CLI labeling tool. '
    'Bổ sung 500 fake reviews từ GPT-generated.'
)
add_paragraph('Dataset cuối cùng (~2000 samples):', bold=True)
add_table(
    ['Thành phần', 'Số lượng', 'Nhãn'],
    [
        ['Reviews genuine (label thủ công)', '~500', 'Genuine (1)'],
        ['Reviews suspicious (label thủ công)', '~300', 'Fake (0)'],
        ['GPT-generated fake reviews', '~500', 'Fake (0)'],
        ['GPT-generated spam', '~200', 'Fake (0)'],
        ['Reviews adapt từ Yelp dataset', '~500', 'Cả hai'],
    ]
)
add_paragraph('Chia dữ liệu: 80% train (1600 samples) / 20% test (400 samples)')

add_heading_custom('5.3. Fine-tune PhoBERT', level=2)
add_paragraph('Cấu hình training:', bold=True)
add_table(
    ['Tham số', 'Giá trị', 'Ghi chú'],
    [
        ['Base model', 'vinai/phobert-base', '135M params'],
        ['Task', 'Binary classification', 'genuine vs fake'],
        ['Epochs', '3–5', 'Tránh overfit với dataset nhỏ'],
        ['Batch size', '16', 'RTX 3060 12GB dư sức'],
        ['Learning rate', '2e-5', 'Standard cho BERT fine-tune'],
        ['Max sequence length', '256 tokens', 'Review thường ngắn'],
        ['Optimizer', 'AdamW', 'Default HuggingFace Trainer'],
        ['VRAM sử dụng', '~4–6 GB', 'RTX 3060 12GB'],
        ['Thời gian training', '~30 phút', '5 epochs trên 2000 samples'],
    ]
)
add_paragraph('Metrics đánh giá (target):', bold=True)
add_table(
    ['Metric', 'Target'],
    [
        ['Accuracy', '≥ 85%'],
        ['F1 Score (macro)', '≥ 0.83'],
        ['Precision', '≥ 0.80'],
        ['Recall', '≥ 0.80'],
    ]
)

doc.add_page_break()

# ============================================================
# CHƯƠNG 6: CÔNG NGHỆ SỬ DỤNG
# ============================================================
add_heading_custom('CHƯƠNG 6: CÔNG NGHỆ SỬ DỤNG', level=1)

add_table(
    ['Tầng', 'Công nghệ', 'Phiên bản', 'Mục đích'],
    [
        ['Frontend', 'React', '18.x', 'Xây dựng giao diện SPA'],
        ['Frontend', 'Vite', '5.x', 'Build tool, Hot Module Replacement'],
        ['Frontend', 'TailwindCSS', '3.x', 'CSS framework utility-first'],
        ['Frontend', 'Recharts', '2.x', 'Biểu đồ phân bố trust score'],
        ['Backend', 'FastAPI', '0.110+', 'REST API framework (Python)'],
        ['Backend', 'SQLAlchemy', '2.x', 'ORM, tương tác database'],
        ['ML', 'PyTorch', '2.x', 'ML framework'],
        ['ML', 'HuggingFace Transformers', '4.x', 'Load và fine-tune PhoBERT'],
        ['ML', 'PhoBERT', 'vinai/phobert-base', 'NLP model cho tiếng Việt'],
        ['NLP', 'datasketch', '-', 'SimHash cho copy-paste detection'],
        ['Scraping', 'Playwright', '1.x', 'Headless browser scrape Google Maps'],
        ['Database', 'PostgreSQL', '16', 'Cơ sở dữ liệu chính'],
        ['Deploy', 'Docker Compose', '-', 'Container hóa toàn bộ hệ thống'],
        ['Hosting', 'Railway / Render', 'Free tier', 'Deploy demo'],
    ]
)

doc.add_page_break()

# ============================================================
# CHƯƠNG 7: KẾ HOẠCH THỰC HIỆN
# ============================================================
add_heading_custom('CHƯƠNG 7: KẾ HOẠCH THỰC HIỆN', level=1)

add_table(
    ['Tuần', 'Công việc', 'Output'],
    [
        ['1–2', 'Scrape data Google Maps + Foody (2000+ reviews)', 'Dataset thô (JSONL files)'],
        ['3', 'Gán nhãn thủ công + generate fake reviews bằng GPT', 'Dataset hoàn chỉnh (~2000 labeled)'],
        ['4', 'Fine-tune PhoBERT, đánh giá model', 'Model .pt + metrics report'],
        ['5–6', 'Xây dựng Backend: FastAPI, scoring engine, database', 'API chạy được, Swagger docs'],
        ['7–8', 'Xây dựng Frontend: 2 trang + UI components', 'Web app hoàn chỉnh'],
        ['9', 'Tích hợp end-to-end, testing', 'Hệ thống chạy đầy đủ'],
        ['10', 'Deploy, viết báo cáo, chuẩn bị demo', 'Link demo + báo cáo đồ án'],
    ]
)

doc.add_page_break()

# ============================================================
# CHƯƠNG 8: TÀI LIỆU THAM KHẢO
# ============================================================
add_heading_custom('CHƯƠNG 8: TÀI LIỆU THAM KHẢO', level=1)

references = [
    '[1] Jindal, N., & Liu, B. (2008). "Opinion Spam and Analysis." Proceedings of the International Conference on Web Search and Data Mining (WSDM).',
    '[2] Ott, M., Choi, Y., Cardie, C., & Hancock, J.T. (2011). "Finding Deceptive Opinion Spam by Any Stretch of the Imagination." Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics (ACL).',
    '[3] Mukherjee, A., Venkataraman, V., Liu, B., & Glance, N. (2013). "What Yelp Fake Review Filter Might Be Doing?" Proceedings of the 7th International AAAI Conference on Weblogs and Social Media (ICWSM).',
    '[4] Li, J., Ott, M., Cardie, C., & Hovy, E. (2014). "Towards a General Rule for Identifying Deceptive Opinion Spam." Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics (ACL).',
    '[5] Rayana, S., & Akoglu, L. (2015). "Collective Opinion Spam Detection: Bridging Review Networks and Metadata." Proceedings of the 21st ACM SIGKDD International Conference on Knowledge Discovery and Data Mining.',
    '[6] Devlin, J., Chang, M.W., Lee, K., & Toutanova, K. (2019). "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." Proceedings of NAACL-HLT.',
    '[7] Nguyen, D.Q., & Nguyen, A.T. (2020). "PhoBERT: Pre-trained language models for Vietnamese." Findings of the Association for Computational Linguistics: EMNLP 2020.',
    '[8] Van Nguyen, K., et al. (2020). "UIT-VSFC: Vietnamese Students\' Feedback Corpus for Sentiment Analysis." Proceedings of RIVF 2018.',
]
for ref in references:
    p = doc.add_paragraph(ref)
    p.paragraph_format.space_after = Pt(6)
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

# ============================================================
# SAVE
# ============================================================
output_path = os.path.join(os.path.dirname(__file__), 'ReviewTrust_Proposal.docx')
doc.save(output_path)
print(f'Saved to {output_path}')
