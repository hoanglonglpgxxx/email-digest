import math
from collections import Counter
from urllib.parse import urlparse


def calculate_entropy(text):
    """Tính độ hỗn loạn của chuỗi ký tự"""
    if not text: return 0
    counter = Counter(text)
    length = len(text)
    entropy = 0
    for count in counter.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def extract_features(url):
    parsed = urlparse(url)

    # 1. Các đặc trưng cơ bản
    url_len = len(url)
    num_digits = sum(c.isdigit() for c in url)
    num_params = len(parsed.query.split('&')) if parsed.query else 0

    # 2. Đặc trưng ký tự đặc biệt (Dấu hiệu của query string phức tạp)
    special_chars = sum(1 for c in url if c in "?&=%-_")

    # 3. Entropy (Link quảng cáo thường có mã hash ngẫu nhiên -> Entropy cao)
    # Ví dụ: "ads?id=hkjshf78" entropy cao hơn "images/avatar.jpg"
    entropy = calculate_entropy(url)

    # 4. Keyword Check (Vẫn giữ nhưng chỉ là phụ trợ)
    has_ad_keyword = 1 if any(x in url.lower() for x in ["ad", "banner", "pixel", "track", "pop", "click"]) else 0

    # 5. Third-party Check (Giả lập)
    # Trong thực tế, extension sẽ so sánh domain của link với domain của web
    # Ở đây ta check domain có thuộc danh sách server quảng cáo nổi tiếng không
    ad_domains = ["doubleclick", "googlead", "facebook", "analytics", "adsystem", "criteo"]
    is_known_ad_domain = 1 if any(d in parsed.netloc for d in ad_domains) else 0

    return {
        "url_length": url_len,
        "num_digits": num_digits,
        "num_params": num_params,
        "special_chars": special_chars,
        "entropy": float(entropy),  # Feature cực mạnh
        "has_ad_keyword": has_ad_keyword,
        "is_known_ad_domain": is_known_ad_domain
    }