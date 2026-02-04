import math
import re
from collections import Counter
from urllib.parse import urlparse


def calculate_entropy(text):
    if not text: return 0
    counter = Counter(text)
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counter.values())


def extract_features_v2(url, is_ad_label=0):
    parsed = urlparse(url)

    # 1. Thông tin cơ bản
    domain = parsed.netloc
    path = parsed.path
    path_depth = len([x for x in path.split('/') if x])  # Độ sâu của thư mục

    # 2. Kích thước (Bóc tách từ URL bằng Regex)
    # Tìm dạng 1200x110 hoặc 300x250 trong URL
    dim_match = re.search(r'(\d+)x(\d+)', url.lower())
    width = int(dim_match.group(1)) if dim_match else 0
    height = int(dim_match.group(2)) if dim_match else 0
    aspect_ratio = round(width / height, 2) if height > 0 else 0

    # 3. Đặc trưng số học
    url_len = len(url)
    num_digits = sum(c.isdigit() for c in url)
    num_params = len(parsed.query.split('&')) if parsed.query else 0

    # 4. Keyword & Type
    has_ad_keyword = 1 if any(x in url.lower() for x in ["ad", "banner", "pixel", "bet", "click"]) else 0
    # Giả định request_type dựa trên đuôi file
    request_type = "image" if any(url.lower().endswith(x) for x in [".gif", ".jpg", ".png", ".webp"]) else "other"

    return {
        "url": url,
        "domain": domain,
        "path_depth": path_depth,
        "url_length": url_len,
        "num_digits": num_digits,
        "num_params": num_params,
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio,
        "request_type": request_type,
        "has_ad_keyword": has_ad_keyword,
        "is_ad": is_ad_label
    }