"""
Aspect extraction cho review tiếng Việt.
Trích xuất 5 khía cạnh: đồ ăn, dịch vụ, giá cả, không gian, vị trí.
Rule-based bằng keyword matching.
"""

import re

# ── Keyword dictionaries ───────────────────────────────────────────────────────

FOOD_KEYWORDS = {
    # Tên món
    "phở", "bún", "bánh", "cơm", "mì", "hủ tiếu", "gà", "bò", "heo", "cá",
    "tôm", "cua", "mực", "rau", "salad", "pizza", "burger", "lẩu", "nướng",
    "chiên", "xào", "luộc", "hấp", "soup", "cháo", "xôi", "chè", "kem",
    "cà phê", "trà", "nước", "sinh tố", "smoothie",
    # Chất lượng đồ ăn
    "ngon", "dở", "tệ", "tươi", "cũ", "tanh", "hôi", "mặn", "nhạt", "cay",
    "ngọt", "chua", "đắng", "béo", "giòn", "mềm", "dai", "nóng", "nguội",
    "thơm", "hương vị", "vị", "khẩu vị", "đậm đà", "thanh",
}

SERVICE_KEYWORDS = {
    "nhân viên", "phục vụ", "phục vụ viên", "bồi bàn", "thu ngân",
    "thái độ", "niềm nở", "thân thiện", "lịch sự", "vô lễ", "thô lỗ",
    "chờ", "chờ đợi", "lâu", "nhanh", "chậm", "tốc độ", "phục vụ nhanh",
    "order", "gọi món", "đặt món", "thanh toán", "hóa đơn",
}

PRICE_KEYWORDS = {
    "giá", "rẻ", "mắc", "đắt", "hợp lý", "xứng đáng", "đáng tiền",
    "giá cả", "giá tiền", "tiền", "chi phí", "budget", "túi tiền",
}
PRICE_PATTERNS = [
    r"\d+\s*k\b",           # 25k
    r"\d+\s*nghìn",         # 25 nghìn
    r"\d+\s*đồng",          # 25000 đồng
    r"\d+\.\d+\s*k",        # 2.5k
    r"\d{2,}\.\d{3}",       # 25.000
]

AMBIANCE_KEYWORDS = {
    "không gian", "atmosphere", "decor", "trang trí", "đẹp", "xấu",
    "sạch", "bẩn", "thoáng", "chật", "hẹp", "rộng", "ồn", "yên tĩnh",
    "máy lạnh", "điều hòa", "nóng", "mát", "bàn", "ghế", "ánh sáng",
    "view", "cảnh", "chỗ ngồi", "tầng", "lầu", "ngoài trời", "trong nhà",
    "thích hợp", "lãng mạn", "ấm cúng", "hiện đại", "vintage",
}

LOCATION_KEYWORDS = {
    "vị trí", "địa điểm", "đường", "phố", "quận", "huyện", "gần", "xa",
    "dễ tìm", "khó tìm", "bản đồ", "google maps", "đỗ xe", "gửi xe",
    "parking", "taxi", "grab", "xe buýt", "đi bộ", "trung tâm",
}


def _text_to_lower_tokens(text: str) -> set[str]:
    text = text.lower()
    # Tách thành bigrams và trigrams + từ đơn để match phrases
    words = text.split()
    tokens = set(words)
    for i in range(len(words) - 1):
        tokens.add(f"{words[i]} {words[i+1]}")
    for i in range(len(words) - 2):
        tokens.add(f"{words[i]} {words[i+1]} {words[i+2]}")
    return tokens


def extract_aspects(text: str) -> list[str]:
    """
    Trích xuất danh sách aspect được đề cập trong review.

    Returns: list các aspect trong ["đồ ăn", "dịch vụ", "giá cả", "không gian", "vị trí"]
    """
    tokens = _text_to_lower_tokens(text)
    text_lower = text.lower()
    found = []

    if tokens & FOOD_KEYWORDS:
        found.append("đồ ăn")

    if tokens & SERVICE_KEYWORDS:
        found.append("dịch vụ")

    has_price_keyword = bool(tokens & PRICE_KEYWORDS)
    has_price_pattern = any(re.search(p, text_lower) for p in PRICE_PATTERNS)
    if has_price_keyword or has_price_pattern:
        found.append("giá cả")

    if tokens & AMBIANCE_KEYWORDS:
        found.append("không gian")

    if tokens & LOCATION_KEYWORDS:
        found.append("vị trí")

    return found


def aspect_bonus(aspects: list[str]) -> int:
    """
    Tính điểm bonus/penalty dựa trên số lượng aspect.
    """
    n = len(aspects)
    if n >= 3:
        return 15
    elif n == 2:
        return 10
    elif n == 1:
        return 0
    else:
        return -15  # Không có aspect nào — generic review
